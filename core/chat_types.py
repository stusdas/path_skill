from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

ConversationType = Literal['standard', 'private']
MainMode = Literal['normal', 'deep_understanding', 'decision_support']
SubMode = Optional[Literal['self_opposition', 'multi_role']]
MessageRole = Literal['user', 'assistant', 'system', 'card']

class ChatMessage(BaseModel):
    role: MessageRole
    content: Any
    avatar: Optional[str] = None
    created_at: Optional[str] = None

class AnalysisState(BaseModel):
    active: bool = False
    analysis_type: Optional[str] = None
    stage: Optional[str] = None
    stage_index: int = 0
    topic: Optional[str] = None
    waiting_for_user: bool = False
    card_emitted: bool = False
    slot_fill: Dict[str, bool] = Field(default_factory=dict)

class CurrentSnapshot(BaseModel):
    emotion_state: str = 'stable'
    decision_state: str = 'none'
    life_phase: str = 'stable_phase'
    confidence: float = 0.5
    updated_at: Optional[str] = None

class DynamicMemoryItem(BaseModel):
    id: str
    summary: str
    type: str
    confidence: str = 'medium'
    created_at: Optional[str] = None

class Conversation(BaseModel):
    id: str
    title: str
    type: ConversationType = 'standard'
    updated_at: str
    active_main_mode: MainMode = 'normal'
    active_sub_mode: SubMode = None
    messages: List[ChatMessage] = Field(default_factory=list)
    analysis_state: AnalysisState = Field(default_factory=AnalysisState)
    short_term_memory: Dict[str, Any] = Field(default_factory=dict)
    is_pinned: bool = False

class UserMemory(BaseModel):
    static_profile_summary: str = '尚未建立长期画像。'
    dynamic_memory: List[DynamicMemoryItem] = Field(default_factory=list)
    current_snapshot: CurrentSnapshot = Field(default_factory=CurrentSnapshot)

class AppSettings(BaseModel):
    api_key: str = ''
    base_url: str = 'https://api.deepseek.com/v1'
    model: str = 'deepseek-chat'
    mock_mode: bool = True

class NewConversationRequest(BaseModel):
    title: Optional[str] = None
    conversation_type: ConversationType = 'standard'

class SendMessageRequest(BaseModel):
    conversation_id: str
    message: str
    api_key: str = ''
    base_url: str = 'https://api.deepseek.com/v1'
    model: str = 'deepseek-chat'
    mock: bool = False
    main_mode: Optional[MainMode] = None
    sub_mode: SubMode = None

class ToggleModeRequest(BaseModel):
    conversation_id: str
    main_mode: MainMode
    sub_mode: SubMode = None

class UpdateConversationTypeRequest(BaseModel):
    conversation_id: str
    conversation_type: ConversationType

class SaveSettingsRequest(BaseModel):
    api_key: str = ''
    base_url: str = 'https://api.deepseek.com/v1'
    model: str = 'deepseek-chat'
    mock_mode: bool = False

class RenameConversationRequest(BaseModel):
    conversation_id: str
    title: str

class TogglePinRequest(BaseModel):
    conversation_id: str
    is_pinned: bool
