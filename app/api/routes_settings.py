from fastapi import APIRouter
from core.chat_types import SaveSettingsRequest
from controllers.settings_controller import SettingsController

router = APIRouter()
controller = SettingsController()

@router.get('/settings')
def get_settings():
    return controller.get().model_dump()

@router.post('/settings')
def save_settings(payload: SaveSettingsRequest):
    return controller.save(payload).model_dump()

@router.get('/config/defaults')
def get_defaults():
    return controller.defaults()
