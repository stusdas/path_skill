from pathlib import Path
from core.chat_types import CurrentSnapshot
from core.config import SNAPSHOTS_DIR
from core.utils import dump_json, load_json, now_iso

SNAPSHOT_FILE = SNAPSHOTS_DIR / 'current_snapshot.json'


def load_snapshot() -> CurrentSnapshot:
    data = load_json(SNAPSHOT_FILE, default=None)
    return CurrentSnapshot(**data) if data else CurrentSnapshot(updated_at=now_iso())


def save_snapshot(snapshot: CurrentSnapshot) -> Path:
    if not snapshot.updated_at:
        snapshot.updated_at = now_iso()
    dump_json(SNAPSHOT_FILE, snapshot.model_dump())
    return SNAPSHOT_FILE
