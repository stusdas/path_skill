import json
import uuid
from core.chat_types import (
    Conversation,
    ChatMessage,
    NewConversationRequest,
    ToggleModeRequest,
    SendMessageRequest,
    DynamicMemoryItem,
    UpdateConversationTypeRequest,
    RenameConversationRequest,
    TogglePinRequest,
)
from core.utils import now_iso, dump_json, load_json
from core.config import APP_STATE_PATH, STATIC_PROFILE_PATH
from core.llm_client import LLMClient
from memory.conversation_store import list_conversations, load_conversation, save_conversation, delete_conversation
from memory.user_memory_store import load_user_memory
from memory.dynamic_memory_store import save_dynamic_memory
from memory.snapshot_store import save_snapshot
from memory.short_term_store import update_short_term_memory
from state.mode_router import ModeRouter
from state.analysis_state_machine import AnalysisStateMachine
from orchestration.context_selector import BackgroundContextSelector
from orchestration.prompt_orchestrator import PromptOrchestrator
from orchestration.card_controller import CardController
from orchestration.decision_pack_builder import DecisionPackBuilder


class ConversationController:
    def __init__(self):
        self.mode_router = ModeRouter()
        self.analysis_machine = AnalysisStateMachine()
        self.context_selector = BackgroundContextSelector()
        self.prompt_orchestrator = PromptOrchestrator()
        self.card_controller = CardController()

    def _export_conversation(self, conv: Conversation):
        return {
            'id': conv.id,
            'title': conv.title,
            'type': conv.type,
            'updated_at': conv.updated_at,
            'main_mode': conv.active_main_mode,
            'sub_mode': conv.active_sub_mode,
            'messages': [m.model_dump() for m in conv.messages],
            'analysis_state': conv.analysis_state.model_dump(),
        }

    def list(self):
        return {'items': [self._export_conversation(c) for c in list_conversations()]}

    def create(self, payload: NewConversationRequest):
        conv = Conversation(
            id=str(uuid.uuid4()),
            title=payload.title or ('不留痕聊天' if payload.conversation_type == 'private' else '新的会话'),
            type=payload.conversation_type,
            updated_at=now_iso(),
        )
        save_conversation(conv)
        dump_json(APP_STATE_PATH, {'last_opened_conversation_id': conv.id})
        return conv

    def get(self, conversation_id: str):
        return load_conversation(conversation_id)

    def toggle_mode(self, payload: ToggleModeRequest):
        conv = load_conversation(payload.conversation_id)
        conv.active_main_mode = payload.main_mode
        conv.active_sub_mode = payload.sub_mode
        conv.analysis_state = self.analysis_machine.deactivate(conv.analysis_state)
        conv.updated_at = now_iso()
        save_conversation(conv)
        return conv

    def update_type(self, payload: UpdateConversationTypeRequest):
        conv = load_conversation(payload.conversation_id)
        conv.type = payload.conversation_type
        conv.updated_at = now_iso()
        save_conversation(conv)
        return conv

    def rename(self, payload: RenameConversationRequest):
        conv = load_conversation(payload.conversation_id)
        conv.title = payload.title
        conv.updated_at = now_iso()
        save_conversation(conv)
        return conv

    def delete(self, conversation_id: str):
        return delete_conversation(conversation_id)

    def toggle_pin(self, payload: TogglePinRequest):
        conv = load_conversation(payload.conversation_id)
        conv.is_pinned = payload.is_pinned
        # We don't necessarily update updated_at for pinning to keep temporal order
        save_conversation(conv)
        return conv

    async def _maybe_auto_rename(self, conv: Conversation, llm: LLMClient, message_text: str):
        # Only rename if title is default
        if conv.title not in ['新的会话', '不留痕聊天', 'New Conversation']:
            return
        
        # Don't rename private chats if they are meant to stay private
        if conv.type == 'private':
            return

        system_prompt = self.prompt_orchestrator.get_title_generator_prompt()
        user_prompt = f"用户的第一条消息是：\"{message_text}\"\n请根据这条消息生成一个简短的标题。"
        
        try:
            new_title = await llm.async_complete(system_prompt, user_prompt, temperature=0.7)
            new_title = new_title.strip().strip('"').strip('【').strip('】').split('\n')[0]
            # Clean up: sometimes LLM adds "标题：" prefix
            if "：" in new_title[:5]:
                new_title = new_title.split("：", 1)[1]
            if ":" in new_title[:5]:
                new_title = new_title.split(":", 1)[1]
                
            if new_title and len(new_title) > 1:
                conv.title = new_title[:30] # Limit length
                save_conversation(conv)
        except Exception:
            pass # Silent fail for auto-rename

    def _load_static_profile(self):
        return load_json(STATIC_PROFILE_PATH, default={}) or {}

    def _maybe_build_analysis_pack(self, conv: Conversation, llm: LLMClient, message_text: str):
        if conv.active_main_mode != 'decision_support':
            return None
        include_roles = conv.active_sub_mode == 'multi_role'
        cache = conv.short_term_memory.get('analysis_pack_cache')
        if cache and cache.get('question') == message_text and cache.get('include_roles') == include_roles:
            return cache.get('pack')
        builder = DecisionPackBuilder(llm)
        pack = builder.build(message_text, include_roles=include_roles)
        conv.short_term_memory['analysis_pack_cache'] = {
            'question': message_text,
            'include_roles': include_roles,
            'pack': pack,
            'updated_at': now_iso(),
        }
        return pack

    def _build_user_prompt(self, message_text: str, context_bundle: dict, conv: Conversation, analysis_pack: dict | None = None):
        static_profile = self._load_static_profile()
        executive_summary = static_profile.get('executive_summary', context_bundle['static_profile_summary'])
        prompt = (
            f"当前主模式：{conv.active_main_mode}\n"
            f"当前二级能力：{conv.active_sub_mode or '无'}\n"
            f"当前分析阶段：{conv.analysis_state.stage or '无'}\n"
            f"长期画像摘要：{executive_summary}\n"
            f"动态记忆：{context_bundle['dynamic_memory']}\n"
            f"当前状态快照：{context_bundle['snapshot']}\n"
            f"当前会话短期记忆：{context_bundle['short_term_memory']}\n"
            f"最近消息：{context_bundle['messages_tail']}\n"
        )
        if static_profile:
            prompt += (
                f"\n画像要点：\n"
                f"- human_info_card: {static_profile.get('human_info_card', {})}\n"
                f"- behavior_patterns: {static_profile.get('behavior_patterns', {})}\n"
                f"- implicit_beliefs: {static_profile.get('implicit_beliefs', {})}\n"
                f"- four_layer_system: {static_profile.get('four_layer_system', {})}\n"
            )
        if analysis_pack:
            prompt += (
                f"\n决策分析包：\n{analysis_pack}\n"
                f"请把这些结构化结果转成自然中文聊天回复，不要机械朗读 JSON。\n"
            )
        prompt += f"\n用户本轮输入：{message_text}\n请严格按照当前模式与阶段回复。"
        return prompt

    async def send_message(self, payload: SendMessageRequest):
        conv = load_conversation(payload.conversation_id)
        if payload.main_mode:
            conv.active_main_mode = payload.main_mode
        if payload.sub_mode is not None:
            conv.active_sub_mode = payload.sub_mode

        user_memory = load_user_memory()
        llm = LLMClient(api_key=payload.api_key, base_url=payload.base_url, model=payload.model, mock=payload.mock)

        conv.messages.append(ChatMessage(role='user', content=payload.message, created_at=now_iso()))
        route = self.mode_router.route(conv.active_main_mode, conv.active_sub_mode, conv.analysis_state, payload.message)
        conv.analysis_state = self.analysis_machine.initialize_if_needed(conv.analysis_state, conv.active_main_mode, conv.active_sub_mode, payload.message[:80])
        context_bundle = self.context_selector.select(conv.active_main_mode, conv.active_sub_mode, user_memory, conv)
        try:
            import asyncio
            # Run the synchronous DecisionPackBuilder in a separate thread to avoid blocking the event loop
            analysis_pack = await asyncio.to_thread(self._maybe_build_analysis_pack, conv, llm, payload.message)

            system_prompt = self.prompt_orchestrator.choose_reply_prompt(conv.active_main_mode, conv.active_sub_mode)
            user_prompt = self._build_user_prompt(payload.message, context_bundle, conv, analysis_pack=analysis_pack)
            
            if analysis_pack and analysis_pack.get('agent_views'):
                agent_mapping = {
                    "current_self": "当下的你",
                    "future_self": "未来的你",
                    "rational_mentor": "理性导师",
                    "emotional_supporter": "情绪支持者"
                }
                for key, content in analysis_pack['agent_views'].items():
                    if content:
                        agent_name = agent_mapping.get(key, key)
                        msg = ChatMessage(role='assistant', content=content, avatar=agent_name, created_at=now_iso())
                        conv.messages.append(msg)
                        yield json.dumps({"type": "agent_bubble", "agent_name": agent_name, "content": content}, ensure_ascii=False) + "\n"

            full_reply = ""
            async for chunk in llm.async_complete_stream(system_prompt, user_prompt, temperature=0.25):
                full_reply += chunk
                yield json.dumps({"type": "text", "content": chunk}, ensure_ascii=False) + "\n"

            reply_text = full_reply
            conv.messages.append(ChatMessage(role='assistant', content=reply_text, created_at=now_iso()))

            conv.analysis_state = self.analysis_machine.advance(conv.analysis_state)
            card = self.card_controller.maybe_emit(conv.analysis_state, analysis_pack=analysis_pack)
            if card:
                conv.messages.append(ChatMessage(role='card', content=card, created_at=now_iso()))

            update_short_term_memory(conv)

            latest_text = payload.message
            if any(k in latest_text for k in ['焦虑', '怕', '担心', '纠结', '选错', '后悔']):
                user_memory.current_snapshot.emotion_state = 'anxious'
                user_memory.current_snapshot.decision_state = 'repeatedly_stuck'
                user_memory.current_snapshot.life_phase = 'turning_point'
                user_memory.current_snapshot.confidence = 0.78
                user_memory.current_snapshot.updated_at = now_iso()
                save_snapshot(user_memory.current_snapshot)

            if conv.type != 'private' and any(k in latest_text for k in ['考研', '找工作', '成长', '稳定', '纠结', '后悔']):
                summary = '最近多次提到在成长、稳定与后悔风险之间反复拉扯。'
                if not any(x.summary == summary for x in user_memory.dynamic_memory):
                    user_memory.dynamic_memory.append(DynamicMemoryItem(id=f'dyn_{len(user_memory.dynamic_memory)+1}', summary=summary, type='repeated_theme', confidence='high', created_at=now_iso()))
                    save_dynamic_memory(user_memory.dynamic_memory)

            if len(conv.messages) <= 3: # Only try on first round
                await self._maybe_auto_rename(conv, llm, payload.message)

            conv.updated_at = now_iso()
            save_conversation(conv)
            dump_json(APP_STATE_PATH, {'last_opened_conversation_id': conv.id})
            
            yield json.dumps({
                "type": "final",
                "conversation": self._export_conversation(conv),
                "reply": reply_text,
                "card": card,
                "suggest_deeper": route['suggest_deeper'],
                "user_memory": user_memory.model_dump(),
                "analysis_pack": analysis_pack,
            }, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "message": f"流式回复异常: {str(e)}"}, ensure_ascii=False) + "\n"
