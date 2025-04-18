import json
import os
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fasthtml.common import Button, FastHTML, Form, Input, RedirectResponse, Titled
from fastlite import database
from openai import AsyncOpenAI

from auth import auth_bware, auth_user, update_session
from components.chat import page
from utils.db import Conversation
from utils.streaming import generate_stream_response

db = database("data/test.db")

dt = db.create(Conversation, pk="id")

app = FastHTML(before=auth_bware)
# app = FastHTML(debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


openai_client = AsyncOpenAI()


static_dir = os.path.join(os.path.dirname(__file__), "static")
light_icon = os.path.join(static_dir, "favicon-light.ico")
dark_icon = os.path.join(static_dir, "favicon-dark.ico")


@app.get("/")
def home(conversation_id: int):
    """Render homepage with FastGPT UI."""

    # reset conversation state for now every time we load the page
    dt.update(id=conversation_id, messages=None)

    home_text = f"""
## InterroGPT - A ChatGPT Implementation Using FastHTML
{dt[conversation_id]}
    """

    return page(home_text)


@app.get("/login")
def login(request, conversation_id: int):
    # Create a login form with token input and preserve conversation_id
    form = Form(
        Input(id="token", name="token", placeholder="Enter your token"),
        Input(type="hidden", name="conversation_id", value=str(conversation_id)),
        Button("Login", type="submit"),
        method="post",
        action="/login",
    )
    return Titled("Login", form)


@app.post("/login")
async def login_post(request, session):
    form = await request.form()
    token = form.get("token")
    conversation_id = form.get("conversation_id")

    # Try to authenticate with the token
    auth_result = auth_user(token)
    if auth_result:
        update_session(session, auth_result)
        return RedirectResponse(f"/?conversation_id={conversation_id}", status_code=303)
    else:
        # If authentication fails, redirect back to login with conversation_id
        return RedirectResponse(
            f"/login?conversation_id={conversation_id}", status_code=303
        )


@app.get("/stream")
async def stream_response(request, message: str, session_id: str = None):
    """Stream responses for the given user input.

    This endpoint is called from the frontend JavaScript in ./components/chat/script.py when a user sends a message.
    The frontend uses EventSource to establish a Server-Sent Events (SSE) connection and streams
    the AI's response in real-time. The session_id is used to maintain conversation context.
    """
    if not message:
        raise HTTPException(status_code=400, detail="Message parameter is required")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    return await generate_stream_response(
        request=request,
        message=message,
        session_id=session_id,
        dt=dt,
        openai_client=openai_client,
    )


# @app.get("/reset")
# def reset_conversation(session_id: str):
#     """Reset the conversation for the specified session ID."""
#     if session_id in conversations:
#         del conversations[session_id]
#     return {"message": "Conversation reset."}


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
