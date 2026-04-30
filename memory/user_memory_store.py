from core.chat_types import UserMemory, DynamicMemoryItem
from core.config import STATIC_PROFILE_PATH
from core.utils import load_json
from memory.dynamic_memory_store import load_dynamic_memory
from memory.snapshot_store import load_snapshot


def load_user_memory() -> UserMemory:
    static_profile = load_json(STATIC_PROFILE_PATH, default=None)
    summary = '尚未建立长期画像。'
    if static_profile:
        summary = static_profile.get('executive_summary', '已建立长期画像。')
    return UserMemory(
        static_profile_summary=summary,
        dynamic_memory=load_dynamic_memory(),
        current_snapshot=load_snapshot(),
    )
