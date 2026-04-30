import json
from core.prompt_loader import load_prompt
from skills.skill_base import SkillBase


class ReportGenerateSkill(SkillBase):
    def run(self, profile: dict, question: str, decomposition: dict, options: dict, alignment: dict, regret: dict, future_sim: dict, agent_views: dict) -> str:
        system_prompt = load_prompt("decision/final_report.md")
        user_prompt = f"用户画像：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n问题：\n{question}\n\n问题拆解：\n{json.dumps(decomposition, ensure_ascii=False, indent=2)}\n\n候选方案：\n{json.dumps(options, ensure_ascii=False, indent=2)}\n\n价值一致性：\n{json.dumps(alignment, ensure_ascii=False, indent=2)}\n\n后悔风险：\n{json.dumps(regret, ensure_ascii=False, indent=2)}\n\n未来模拟：\n{json.dumps(future_sim, ensure_ascii=False, indent=2)}\n\n多角色观点：\n{json.dumps(agent_views, ensure_ascii=False, indent=2)}"
        return self.llm.complete(system_prompt, user_prompt, temperature=0.35)
