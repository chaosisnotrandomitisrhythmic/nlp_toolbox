from dataclasses import dataclass


@dataclass
class Conversation:
    id: int
    messages: str
    created_at: str
    interro_selection: str
    user_id: str
