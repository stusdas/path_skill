from fastapi import APIRouter, HTTPException
from core.chat_types import (
    NewConversationRequest, SendMessageRequest, ToggleModeRequest, 
    UpdateConversationTypeRequest, RenameConversationRequest, TogglePinRequest
)
from controllers.conversation_controller import ConversationController

router = APIRouter()
controller = ConversationController()

@router.get('/conversations')
def list_conversations():
    return controller.list()

@router.post('/conversations/new')
def new_conversation(payload: NewConversationRequest):
    return controller.create(payload).model_dump()

@router.get('/conversations/{conversation_id}')
def get_conversation(conversation_id: str):
    try:
        return controller._export_conversation(controller.get(conversation_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='conversation not found')

@router.post('/conversations/toggle-mode')
def toggle_mode(payload: ToggleModeRequest):
    return controller._export_conversation(controller.toggle_mode(payload))

@router.post('/conversations/update-type')
def update_type(payload: UpdateConversationTypeRequest):
    return controller._export_conversation(controller.update_type(payload))

@router.post('/conversations/rename-title')
def rename_conversation(payload: RenameConversationRequest):
    return controller._export_conversation(controller.rename(payload))

@router.delete('/conversations/{conversation_id}')
def delete_conversation(conversation_id: str):
    success = controller.delete(conversation_id)
    return {"success": success}

@router.post('/conversations/pin')
def toggle_pin(payload: TogglePinRequest):
    return controller._export_conversation(controller.toggle_pin(payload))

from fastapi.responses import StreamingResponse

@router.post('/chat/send')
async def send_message(payload: SendMessageRequest):
    return StreamingResponse(controller.send_message(payload), media_type='text/event-stream')
