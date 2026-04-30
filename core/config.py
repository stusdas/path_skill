from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / 'app'
PROMPTS_DIR = ROOT_DIR / 'prompts'
DATA_DIR = ROOT_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
PROFILES_DIR = DATA_DIR / 'profiles'
CASES_DIR = DATA_DIR / 'cases'
REPORTS_DIR = DATA_DIR / 'reports'
CONVERSATIONS_DIR = DATA_DIR / 'conversations'
DYNAMIC_MEMORY_DIR = DATA_DIR / 'dynamic_memory'
SNAPSHOTS_DIR = DATA_DIR / 'snapshots'
UPLOADS_DIR = DATA_DIR / 'uploads'
SETTINGS_DIR = DATA_DIR / 'settings'

STATIC_PROFILE_PATH = PROFILES_DIR / 'latest_profile.json'
APP_STATE_PATH = SETTINGS_DIR / 'app_state.json'
API_CONFIG_PATH = SETTINGS_DIR / 'api_config.json'
BUILD_MANIFEST_PATH = ROOT_DIR / 'build_manifest.json'

DEFAULT_BASE_URL = 'https://api.deepseek.com/v1'
DEFAULT_MODEL = 'deepseek-chat'

for _p in [
    DATA_DIR, RAW_DIR, PROCESSED_DIR, PROFILES_DIR, CASES_DIR, REPORTS_DIR,
    CONVERSATIONS_DIR, DYNAMIC_MEMORY_DIR, SNAPSHOTS_DIR, UPLOADS_DIR, SETTINGS_DIR,
]:
    _p.mkdir(parents=True, exist_ok=True)


def ensure_default_settings() -> None:
    if not API_CONFIG_PATH.exists():
        API_CONFIG_PATH.write_text(json.dumps({
            'api_key': '',
            'base_url': DEFAULT_BASE_URL,
            'model': DEFAULT_MODEL,
            'mock_mode': True
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    if not APP_STATE_PATH.exists():
        APP_STATE_PATH.write_text(json.dumps({
            'last_opened_conversation_id': None
        }, ensure_ascii=False, indent=2), encoding='utf-8')

ensure_default_settings()
