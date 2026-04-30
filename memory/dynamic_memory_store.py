from pathlib import Path
from typing import List
from core.chat_types import DynamicMemoryItem
from core.config import DYNAMIC_MEMORY_DIR
from core.utils import dump_json, load_json

MEMORY_FILE = DYNAMIC_MEMORY_DIR / 'global_dynamic_memory.json'


def load_dynamic_memory() -> List[DynamicMemoryItem]:
    data = load_json(MEMORY_FILE, default=[])
    return [DynamicMemoryItem(**item) for item in data]


def save_dynamic_memory(items: List[DynamicMemoryItem]) -> Path:
    dump_json(MEMORY_FILE, [x.model_dump() for x in items])
    return MEMORY_FILE
