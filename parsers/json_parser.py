import json
from parsers.text_parser import read_text_file


def read_json_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return read_text_file(file_path)
