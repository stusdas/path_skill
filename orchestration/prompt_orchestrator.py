from core.prompt_loader import load_prompt


class PromptOrchestrator:
    def choose_reply_prompt(self, main_mode: str, sub_mode: str | None):
        persona = load_prompt('chat/system_persona.md')
        if main_mode == 'normal':
            mode_prompt = load_prompt('chat/normal_chat_reply.md')
        elif main_mode == 'deep_understanding' and sub_mode is None:
            mode_prompt = load_prompt('chat/deep_understanding_reply.md')
        elif main_mode == 'deep_understanding' and sub_mode == 'self_opposition':
            mode_prompt = load_prompt('chat/self_opposition_reply.md')
        elif main_mode == 'decision_support' and sub_mode is None:
            mode_prompt = load_prompt('chat/decision_support_reply.md')
        elif main_mode == 'decision_support' and sub_mode == 'multi_role':
            mode_prompt = load_prompt('chat/multi_role_reply.md')
        else:
            mode_prompt = load_prompt('chat/normal_chat_reply.md')
        return persona + '\n\n' + mode_prompt
    def get_title_generator_prompt(self):
        return load_prompt('chat/session_title_generator.md')
