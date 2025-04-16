import json
import os
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fasthtml.common import A, FastHTML, P, RedirectResponse
from fasthtml.oauth import redir_url
from fastlite import database
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from components.chat import page
from utils.auth import AUTH_CALLBACK_PATH, auth_client, bware
from utils.db import Conversation, update_messages

db = database("data/test.db")

dt = db.create(Conversation, pk="id")

# app = FastHTML(before=bware) disable bware auth and query param saving for now
app = FastHTML(debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


openai_client = AsyncOpenAI()


static_dir = os.path.join(os.path.dirname(__file__), "static")
light_icon = os.path.join(static_dir, "favicon-light.ico")
dark_icon = os.path.join(static_dir, "favicon-dark.ico")


@app.get("/")
def home(session, conversation_id: int):
    """Render homepage with FastGPT UI."""

    # reset conversation state for now every time we load the page
    dt.update(id=conversation_id, messages=None)

    home_text = f"""
## InterroGPT - A ChatGPT Implementation Using FastHTML
{dt[conversation_id]}
    """

    return page(home_text)


@app.get("/stream")
async def stream_response(request, message: str, session_id: str = None):
    """Stream responses for the given user input."""
    if not message:
        raise HTTPException(status_code=400, detail="Message parameter is required")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    if dt[session_id].messages is None:

        messages = update_messages(
            conversation_id=session_id,
            message={
                "role": "system",
                "content": "You are a helpful assistant. Use Markdown for formatting.",
            },
            dt=dt,
        )
        print("System message added to conversation", dt[session_id])

    messages = update_messages(
        conversation_id=session_id,
        message={"role": "user", "content": message},
        dt=dt,
    )
    print("User message added to conversation", dt[session_id])

    async def event_generator():
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=json.loads(dt[session_id].messages),
                stream=True,
            )

            assistant_response = ""

            async for chunk in response:
                if await request.is_disconnected():
                    print(f"Client for session {session_id} disconnected")
                    break

                content = chunk.choices[0].delta.content
                if content:
                    assistant_response += content
                    yield {"data": content}

            messages = update_messages(
                conversation_id=session_id,
                message={"role": "assistant", "content": assistant_response},
                dt=dt,
            )
            print("Assistant message added to conversation", dt[session_id])

        except Exception as e:
            yield {"data": f"Error: {str(e)}"}

        finally:
            print(f"Streaming finished for session {session_id}")

    return EventSourceResponse(event_generator())


# @app.get("/reset")
# def reset_conversation(session_id: str):
#     """Reset the conversation for the specified session ID."""
#     if session_id in conversations:
#         del conversations[session_id]
#     return {"message": "Conversation reset."}


# User asks us to Login
@app.get("/login")
def login(request):
    redir = redir_url(request, AUTH_CALLBACK_PATH)
    login_link = auth_client.login_link(redir)
    return P(A("Login with Hugging Face", href=login_link))


# User comes back to us with an auth code from Hugging Face
@app.get(AUTH_CALLBACK_PATH)
def auth_redirect(code: str, request, session):
    redir = redir_url(request, AUTH_CALLBACK_PATH)
    user_info = auth_client.retr_info(code, redir)
    user_id = user_info[auth_client.id_key]  # get their ID
    session["user_id"] = user_id  # save ID in the session
    return RedirectResponse("/", status_code=303)


@app.post("/conversation")
async def create_conversation(request):
    """Initialize a new conversation in the database."""
    try:
        # Get request body as JSON
        body = await request.json()

        # Add debug logging
        print("Received request body:", body)

        # Validate required fields
        user_id = body.get("user_id")
        interro_selection = body.get("interro_selection")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if not interro_selection:
            raise HTTPException(status_code=400, detail="interro_selection is required")

        try:
            # Create a new conversation record
            conversation = dt.insert(
                Conversation(
                    user_id=user_id,
                    interro_selection=json.dumps(interro_selection),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )

            # Add debug logging
            print("Created conversation:", conversation)

            # Make sure we're returning a proper JSON response
            return {"id": conversation.id, "message": "Conversation initialized"}

        except Exception as db_error:
            print("Database error:", str(db_error))
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(db_error)}"
            )

    except ValueError as ve:
        print("Value error:", str(ve))
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(ve)}")
    except Exception as e:
        print("Unexpected error:", str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to create conversation: {str(e)}"
        )
