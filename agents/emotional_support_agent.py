from agents.base_agent import BaseAgent


class EmotionalSupportAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "agents/emotional_supporter.md")
