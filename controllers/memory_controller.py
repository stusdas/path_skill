from core.utils import load_json
from core.config import STATIC_PROFILE_PATH
from memory.dynamic_memory_store import load_dynamic_memory, save_dynamic_memory
from memory.snapshot_store import load_snapshot
from memory.user_memory_store import load_user_memory


class MemoryController:
    def get_all(self):
        static_profile = load_json(STATIC_PROFILE_PATH, default={}) or {}
        user_memory = load_user_memory()
        return {
            'memory': user_memory.model_dump(),
            'profile': static_profile,
        }

    def delete_dynamic(self, item_id: str):
        items = [x for x in load_dynamic_memory() if x.id != item_id]
        save_dynamic_memory(items)
        return {'ok': True}
