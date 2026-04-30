from core.chat_types import Conversation, UserMemory


class BackgroundContextSelector:
    def select(self, main_mode: str, sub_mode: str | None, memory: UserMemory, conversation: Conversation):
        bundle = {
            'static_profile_summary': memory.static_profile_summary,
            'dynamic_memory': [x.summary for x in memory.dynamic_memory[-5:]],
            'snapshot': memory.current_snapshot.model_dump(),
            'short_term_memory': conversation.short_term_memory,
            'messages_tail': [m.model_dump() for m in conversation.messages[-8:]],
            'focus': 'light_context',
        }
        if main_mode == 'deep_understanding':
            bundle['focus'] = 'behavior_and_beliefs'
        elif main_mode == 'decision_support':
            bundle['focus'] = 'decision_path_and_values'
        if sub_mode == 'self_opposition':
            bundle['focus'] = 'self_opposition'
        elif sub_mode == 'multi_role':
            bundle['focus'] = 'multi_role_decision'
        return bundle
