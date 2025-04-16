from dataclasses import dataclass
from apswutils.db import Table
import json


@dataclass
class Conversation:
    id: int
    messages: str
    created_at: str
    interro_selection: str
    user_id: str


def update_messages(conversation_id: int, message: dict, dt: Table):
    """Update the messages for a conversation in the database.

    Args:
        conversation_id (int): The ID of the conversation to update
        message (dict): The message to append to the conversation. Should follow the OpenAI message schema:
            {
                "role": str,  # "system", "user", or "assistant"
                "content": str  # The actual message content
            }
        dt (Table): The database table containing the conversation

    Returns:
        list: The updated list of messages for the conversation

    Note:
        If there are no existing messages, a new list will be created with the given message
        as its only entry.
    """
    stored_messages = dt[conversation_id].messages
    messages = json.loads(stored_messages) if stored_messages else []
    messages.append(message)
    dt.update(id=conversation_id, messages=json.dumps(messages))
    return messages
