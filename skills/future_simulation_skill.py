import json
from core.prompt_loader import load_prompt
from core.utils import ensure_json
from skills.skill_base import SkillBase


class FutureSimulationSkill(SkillBase):
    def run(self, profile: dict, question: str, decomposition: dict, options: dict, agent_views: dict) -> dict:
        system_prompt = load_prompt("decision/future_simulation.md")
        user_prompt = f"用户画像：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n问题：\n{question}\n\n问题拆解：\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}\n\n候选方案：\n{json.dumps(options, ensure_ascii=False, indent=2)}\n\n多角色观点：\n{json.dumps(agent_views, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.35))
