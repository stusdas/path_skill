import json
from core.prompt_loader import load_prompt
from core.utils import ensure_json
from skills.skill_base import SkillBase


class DecisionDecomposeSkill(SkillBase):
    def run(self, profile: dict, question: str) -> dict:
        system_prompt = load_prompt("decision/decision_decompose.md")
        user_prompt = f"用户画像：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n当前问题：\n{question}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.25))
