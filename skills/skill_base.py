from core.llm_client import LLMClient


class SkillBase:
    def __init__(self, llm: LLMClient):
        self.llm = llm
