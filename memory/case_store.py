from pathlib import Path
from core.config import CASES_DIR
from core.utils import dump_json, load_json


def save_case(case_data: dict, case_name: str) -> Path:
    path = CASES_DIR / f"{case_name}.json"
    dump_json(path, case_data)
    return path


def list_cases() -> list:
    items = []
    for p in sorted(CASES_DIR.glob("*.json")):
        items.append(load_json(p))
    return items
