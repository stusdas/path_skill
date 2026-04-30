import json
from core.prompt_loader import load_prompt
from core.utils import ensure_json


class BaseAgent:
    def __init__(self, llm, prompt_path: str):
        self.llm = llm
        self.prompt_path = prompt_path

    def run(self, profile: dict, question: str, decomposition: dict, options: dict) -> dict:
        system_prompt = load_prompt(self.prompt_path)
        user_prompt = f"用户画像：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n问题：\n{question}\n\n问题拆解：\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}\n\n候选方案：\n{json.dumps(options, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.35))
