from core.chat_types import AppSettings, SaveSettingsRequest
from core.config import DEFAULT_BASE_URL, DEFAULT_MODEL
from memory.settings_store import load_settings, save_settings


class SettingsController:
    def get(self) -> AppSettings:
        return load_settings()

    def save(self, payload: SaveSettingsRequest) -> AppSettings:
        settings = AppSettings(**payload.model_dump())
        return save_settings(settings)

    def defaults(self):
        current = load_settings()
        return {
            'base_url': current.base_url or DEFAULT_BASE_URL,
            'model': current.model or DEFAULT_MODEL,
        }
