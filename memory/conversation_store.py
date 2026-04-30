from pathlib import Path
from typing import List
from core.chat_types import Conversation
from core.config import CONVERSATIONS_DIR
from core.utils import dump_json, load_json


def conversation_path(conversation_id: str) -> Path:
    return CONVERSATIONS_DIR / f'{conversation_id}.json'


def save_conversation(conv: Conversation) -> Path:
    path = conversation_path(conv.id)
    dump_json(path, conv.model_dump())
    return path


def load_conversation(conversation_id: str) -> Conversation:
    data = load_json(conversation_path(conversation_id), default=None)
    if not data:
        raise FileNotFoundError(f'Conversation not found: {conversation_id}')
    return Conversation(**data)


def list_conversations() -> List[Conversation]:
    items = []
    for p in sorted(CONVERSATIONS_DIR.glob('*.json')):
        data = load_json(p, default=None)
        if data:
            items.append(Conversation(**data))
    return sorted(items, key=lambda x: x.updated_at, reverse=True)
