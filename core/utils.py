import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def now_str() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def ensure_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?', '', text).strip()
        text = re.sub(r'```$', '', text).strip()
    
    def try_parse(t: str):
        try:
            v = json.loads(t)
            if isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
                return try_parse(v)
            return v
        except Exception:
            return None

    # 1. Try standard parse
    val = try_parse(text)
    if isinstance(val, dict): return val

    # 2. Try to fix truncated JSON by appending closing characters
    if text.startswith('{'):
        for fix in ['}', '"}', '"]}', '"}]}']:
            val = try_parse(text + fix)
            if isinstance(val, dict): return val

    # 3. Try regex match for any { ... } block
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        val = try_parse(match.group(0))
        if isinstance(val, dict): return val
        
    return {'raw_output': text}


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def truncate_text(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + '\n\n[内容过长，已截断]'
