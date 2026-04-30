import json
from core.prompt_loader import load_prompt
from core.utils import ensure_json
from skills.skill_base import SkillBase


class OptionGenerateSkill(SkillBase):
    def run(self, profile: dict, question: str, decomposition: dict) -> dict:
        system_prompt = load_prompt("decision/option_generation.md")
        user_prompt = f"用户画像：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n问题：\n{question}\n\n问题拆解：\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.3))
