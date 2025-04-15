import os
from datetime import datetime, timezone
import uuid
import time
import json

from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fasthtml.common import (
    A,
    Body,
    Button,
    Div,
    FastHTML,
    Favicon,
    Head,
    Html,
    P,
    RedirectResponse,
    Script,
    Style,
    Textarea,
    Title,
)
from fasthtml.oauth import redir_url
from fastlite import database
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from styles.styles import styles
from utils.auth import AUTH_CALLBACK_PATH, auth_client, bware
from utils.db import Conversation
from utils.script import script
from utils.svg import Path, Svg


db = database("data/test.db")

dt = db.create(Conversation, pk="id")

conversations = {}

# app = FastHTML(before=bware) disable bware auth and query param saving for now
app = FastHTML(debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


openai_client = AsyncOpenAI()


static_dir = os.path.join(os.path.dirname(__file__), "static")
light_icon = os.path.join(static_dir, "favicon-light.ico")
dark_icon = os.path.join(static_dir, "favicon-dark.ico")


@app.get("/")
def home(session):
    """Render homepage with FastGPT UI."""

    home_text = f"""
## InterroGPT - A ChatGPT Implementation Using FastHTML
{session.get("interro_selection", {})}
    """

    page = Html(
        Head(
            Title("InterroGPT"),
            Favicon(
                light_icon="/static/favicon-light.ico",
                dark_icon="/static/favicon-dark.ico",
            ),
            Style(styles),
            # Import libraries for markdown-to-html rendering and sanitization used in script.py
            Script(src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"),
            Script(
                src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/2.2.9/purify.min.js"
            ),
        ),
        Body(
            Div(
                Div("InterroGPT", _class="logo-text"),
                Div(
                    Button(
                        Svg(
                            Path(
                                d="M441 58.9L453.1 71c9.4 9.4 9.4 24.6 0 33.9L424 134.1 377.9 88 407 58.9c9.4-9.4 24.6-9.4 33.9 0zM209.8 256.2L344 121.9 390.1 168 255.8 302.2c-2.9 2.9-6.5 5-10.4 6.1l-58.5 16.7 16.7-58.5c1.1-3.9 3.2-7.5 6.1-10.4zM373.1 25L175.8 222.2c-8.7 8.7-15 19.4-18.3 31.1l-28.6 100c-2.4 8.4-.1 17.4 6.1 23.6s15.2 8.5 23.6 6.1l100-28.6c11.8-3.4 22.5-9.7 31.1-18.3L487 138.9c28.1-28.1 28.1-73.7 0-101.8L474.9 25C446.8-3.1 401.2-3.1 373.1 25zM88 64C39.4 64 0 103.4 0 152L0 424c0 48.6 39.4 88 88 88l272 0c48.6 0 88-39.4 88-88l0-112c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 112c0 22.1-17.9 40-40 40L88 464c-22.1 0-40-17.9-40-40l0-272c0-22.1 17.9-40 40-40l112 0c13.3 0 24-10.7 24-24s-10.7-24-24-24L88 64z",
                                fill="#b4b4b4",
                            ),
                            viewBox="0 0 512 512",
                            _class="refresh-icon",
                        ),
                        onclick="location.reload()",
                        _class="refresh-button",
                    ),
                    _class="refresh-container",
                ),
                _class="header",
            ),
            Div(
                Div(
                    Div(
                        id="home-text-container",
                        _class="markdown-container",
                        **{"data-home-text": home_text},
                    ),
                    _class="title-wrapper",
                ),
                P(id="output"),
                Div(
                    Textarea(
                        id="message",
                        rows=1,
                        cols=50,
                        placeholder="Message FastGPT",
                        oninput="autoResizeTextarea()",
                        onkeypress="checkEnter(event)",
                    ),
                    Button(
                        Svg(
                            Path(
                                d="M214.6 41.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 141.2 160 448c0 17.7 14.3 32 32 32s32-14.3 32-32l0-306.7L329.4 246.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"
                            ),
                            viewBox="0 0 384 512",
                            _class="send-icon",
                        ),
                        onclick="sendMessage()",
                        _class="send-button",
                    ),
                    _class="container",
                ),
                _class="wrapper",
            ),
            Script(script),
        ),
    )
    return page


@app.get("/stream")
async def stream_response(request, message: str, session_id: str = None):
    """Stream responses for the given user input."""
    if not message:
        raise HTTPException(status_code=400, detail="Message parameter is required")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    if session_id not in conversations:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use Markdown for formatting.",
            }
        ]
        conversations[session_id] = messages

    conversations[session_id].append({"role": "user", "content": message})

    async def event_generator():
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini", messages=conversations[session_id], stream=True
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

            conversations[session_id].append(
                {"role": "assistant", "content": assistant_response}
            )

        except Exception as e:
            yield {"data": f"Error: {str(e)}"}

        finally:
            print(f"Streaming finished for session {session_id}")

    return EventSourceResponse(event_generator())


@app.get("/reset")
def reset_conversation(session_id: str):
    """Reset the conversation for the specified session ID."""
    if session_id in conversations:
        del conversations[session_id]
    return {"message": "Conversation reset."}


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
