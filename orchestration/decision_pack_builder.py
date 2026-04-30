from core.utils import load_json
from core.config import STATIC_PROFILE_PATH
from skills.decision_decompose_skill import DecisionDecomposeSkill
from skills.option_generate_skill import OptionGenerateSkill
from skills.value_alignment_skill import ValueAlignmentSkill
from skills.regret_risk_skill import RegretRiskSkill
from skills.future_simulation_skill import FutureSimulationSkill
from agents.current_self_agent import CurrentSelfAgent
from agents.future_self_agent import FutureSelfAgent
from agents.rational_mentor_agent import RationalMentorAgent
from agents.emotional_support_agent import EmotionalSupportAgent


class DecisionPackBuilder:
    def __init__(self, llm):
        self.decompose_skill = DecisionDecomposeSkill(llm)
        self.option_skill = OptionGenerateSkill(llm)
        self.alignment_skill = ValueAlignmentSkill(llm)
        self.regret_skill = RegretRiskSkill(llm)
        self.future_skill = FutureSimulationSkill(llm)
        self.current_agent = CurrentSelfAgent(llm)
        self.future_agent = FutureSelfAgent(llm)
        self.rational_agent = RationalMentorAgent(llm)
        self.emotional_agent = EmotionalSupportAgent(llm)

    def _load_profile(self):
        profile = load_json(STATIC_PROFILE_PATH, default={}) or {}
        if not profile:
            profile = {
                "executive_summary": "尚未建立完整长期画像，当前只能依据有限资料进行阶段性判断。",
                "human_info_card": {},
                "expression_style": {},
                "self_memory": {},
                "behavior_patterns": {},
                "implicit_beliefs": {},
                "four_layer_system": {},
            }
        return profile

    def build(self, question: str, include_roles: bool = False):
        profile = self._load_profile()
        decomposition = self.decompose_skill.run(profile, question)
        options = self.option_skill.run(profile, question, decomposition)
        alignment = self.alignment_skill.run(profile, decomposition, options)
        regret = self.regret_skill.run(profile, decomposition, options)
        agent_views = {}
        if include_roles:
            agent_views = {
                "current_self": self.current_agent.run(profile, question, decomposition, options),
                "future_self": self.future_agent.run(profile, question, decomposition, options),
                "rational_mentor": self.rational_agent.run(profile, question, decomposition, options),
                "emotional_supporter": self.emotional_agent.run(profile, question, decomposition, options),
            }
        future_simulation = self.future_skill.run(profile, question, decomposition, options, agent_views)
        return {
            "profile_summary": profile.get("executive_summary", "已建立长期画像。"),
            "decomposition": decomposition,
            "options": options,
            "alignment": alignment,
            "regret": regret,
            "future_simulation": future_simulation,
            "agent_views": agent_views,
        }
