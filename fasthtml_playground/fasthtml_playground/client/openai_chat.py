import json
from typing import List, Dict, Any, Generator, Optional

from openai import OpenAI
from fasthtml.common import Div, Span


def stream_response_openai(
    messages: List[Dict[str, str]],
    client: OpenAI,
    model_name: str,
    system_prompt: str,
    temperature: float = 0.7,
    user_bubble_class: str = "chat-bubble chat-bubble-primary",
    assistant_bubble_class: str = "chat-bubble chat-bubble-secondary",
    bubble_header: bool = True,
) -> Generator[str, None, None]:
    """
    Stream a response from OpenAI's API and yield HTML chunks.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        client: OpenAI client instance
        model_name: Name of the OpenAI model to use
        system_prompt: System prompt to use for the conversation
        temperature: Temperature parameter for the model
        user_bubble_class: CSS class for user message bubbles
        assistant_bubble_class: CSS class for assistant message bubbles
        bubble_header: Whether to include a header in the message bubbles

    Yields:
        HTML chunks for streaming to the client
    """
    # Prepare the messages with the system prompt
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages)

    # Start the chat completion stream
    stream = client.chat.completions.create(
        model=model_name,
        messages=api_messages,
        temperature=temperature,
        stream=True,
    )

    # Create a container for the assistant's message
    assistant_div = Div(cls=assistant_bubble_class)
    if bubble_header:
        assistant_div.append(Span("Assistant", cls="text-xs opacity-50"))

    # Create a container for the content
    content_div = Div(cls="mt-1")
    assistant_div.append(content_div)

    # Yield the opening div
    yield f'<div id="chatlist" hx-swap-oob="beforeend">{assistant_div.render()}</div>'

    # Process the stream
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            content_div.append(content)
            yield f'<div id="chatlist" hx-swap-oob="beforeend">{content_div.render()}</div>'

    # Yield the closing div
    yield f'<div id="chatlist" hx-swap-oob="beforeend"></div>'
