from pathlib import Path
from core.config import PROFILES_DIR
from core.utils import dump_json, load_json


def save_profile(profile: dict, name: str = "latest_profile") -> Path:
    path = PROFILES_DIR / f"{name}.json"
    dump_json(path, profile)
    return path


def load_profile(name: str = "latest_profile") -> dict:
    return load_json(PROFILES_DIR / f"{name}.json")
