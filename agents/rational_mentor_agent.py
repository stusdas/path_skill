from agents.base_agent import BaseAgent


class RationalMentorAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, "agents/rational_mentor.md")
