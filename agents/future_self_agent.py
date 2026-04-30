from agents.base_agent import BaseAgent


class FutureSelfAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "agents/future_self.md")
