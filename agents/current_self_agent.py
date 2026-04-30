from agents.base_agent import BaseAgent


class CurrentSelfAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "agents/current_self.md")
