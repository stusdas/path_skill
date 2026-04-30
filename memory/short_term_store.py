from core.chat_types import Conversation


def update_short_term_memory(conversation: Conversation) -> dict:
    last_user = ''
    last_ai = ''
    for msg in reversed(conversation.messages):
        if msg.role == 'assistant' and not last_ai:
            last_ai = msg.content
        if msg.role == 'user' and not last_user:
            last_user = msg.content
        if last_user and last_ai:
            break
    conversation.short_term_memory['last_user_message'] = last_user
    conversation.short_term_memory['last_ai_reply'] = last_ai
    conversation.short_term_memory['last_stage'] = conversation.analysis_state.stage
    return conversation.short_term_memory
