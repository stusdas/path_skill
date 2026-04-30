from pathlib import Path
from core.config import PROMPTS_DIR


def load_prompt(relative_path: str, **kwargs) -> str:
    path = PROMPTS_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f'Prompt file not found: {path}')
    text = path.read_text(encoding='utf-8')
    if kwargs:
        return text.format(**kwargs)
    return text
