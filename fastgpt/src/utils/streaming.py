import json

from apswutils.db import Table
from fastapi import HTTPException
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from .db import update_messages


async def generate_stream_response(
    request,
    message: str,
    session_id: str,
    dt: Table,
    openai_client: AsyncOpenAI,
    model: str = "gpt-4o-mini",
):
    """Generate a streaming response for the given user input.

    Args:
        request: The FastAPI request object
        message: The user's message
        session_id: The session ID
        dt: The database table
        openai_client: The OpenAI client
        model: The model to use for completion (default: "gpt-4o-mini")

    Returns:
        EventSourceResponse: The streaming response
    """
    if dt[session_id].messages is None:
        update_messages(
            conversation_id=session_id,
            message={
                "role": "system",
                "content": "You are a helpful assistant. Use Markdown for formatting.",
            },
            dt=dt,
        )
        print("System message added to conversation", dt[session_id])

    update_messages(
        conversation_id=session_id,
        message={"role": "user", "content": message},
        dt=dt,
    )
    print("User message added to conversation", dt[session_id])

    async def event_generator():
        try:
            response = await openai_client.chat.completions.create(
                model=model,
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

            update_messages(
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
