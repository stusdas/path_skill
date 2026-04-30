from app.core.types import Conversation, UserMemory, DynamicMemoryItem

class MemoryManager:
    def update_short_term(self, conversation: Conversation):
        last_user = ""
        last_ai = ""
        for msg in reversed(conversation.messages):
            if msg.role == "assistant" and not last_ai:
                last_ai = msg.content
            if msg.role == "user" and not last_user:
                last_user = msg.content
            if last_user and last_ai:
                break

        conversation.short_term_memory["last_user_message"] = last_user
        conversation.short_term_memory["last_ai_reply"] = last_ai
        conversation.short_term_memory["last_stage"] = conversation.analysis_state.stage
        return conversation.short_term_memory

    def update_snapshot(self, memory: UserMemory, conversation: Conversation):
        latest_user_text = ""
        for msg in reversed(conversation.messages):
            if msg.role == "user":
                latest_user_text = msg.content
                break

        if any(k in latest_user_text for k in ["焦虑", "怕", "担心", "纠结"]):
            memory.current_snapshot.emotion_state = "anxious"
            memory.current_snapshot.decision_state = "repeatedly_stuck"
            memory.current_snapshot.life_phase = "turning_point"
            memory.current_snapshot.confidence = 0.72
        return memory.current_snapshot

    def maybe_update_dynamic_memory(self, memory: UserMemory, conversation: Conversation):
        latest_user_text = ""
        for msg in reversed(conversation.messages):
            if msg.role == "user":
                latest_user_text = msg.content
                break

        triggers = ["考研", "找工作", "成长", "稳定", "纠结"]
        if any(k in latest_user_text for k in triggers):
            summary = "最近多次提到在成长与稳定之间的拉扯。"
            if not any(x.summary == summary for x in memory.dynamic_memory):
                memory.dynamic_memory.append(
                    DynamicMemoryItem(
                        id=f"dyn_{len(memory.dynamic_memory)+1}",
                        summary=summary,
                        type="repeated_theme",
                        confidence="high",
                    )
                )
        return memory.dynamic_memory
