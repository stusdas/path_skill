from core.chat_types import AppSettings
from core.config import API_CONFIG_PATH
from core.utils import dump_json, load_json


def load_settings() -> AppSettings:
    return AppSettings(**(load_json(API_CONFIG_PATH, default={}) or {}))


def save_settings(settings: AppSettings):
    dump_json(API_CONFIG_PATH, settings.model_dump())
    return settings
