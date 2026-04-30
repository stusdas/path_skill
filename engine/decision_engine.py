from datetime import datetime
from pathlib import Path

from agents.current_self_agent import CurrentSelfAgent
from agents.emotional_support_agent import EmotionalSupportAgent
from agents.future_self_agent import FutureSelfAgent
from agents.rational_mentor_agent import RationalMentorAgent
from core.config import REPORTS_DIR
from memory.case_store import save_case
from skills.decision_decompose_skill import DecisionDecomposeSkill
from skills.future_simulation_skill import FutureSimulationSkill
from skills.option_generate_skill import OptionGenerateSkill
from skills.regret_risk_skill import RegretRiskSkill
from skills.report_generate_skill import ReportGenerateSkill
from skills.value_alignment_skill import ValueAlignmentSkill


class DecisionEngine:
    def __init__(self, llm):
        self.decompose_skill = DecisionDecomposeSkill(llm)
        self.option_skill = OptionGenerateSkill(llm)
        self.alignment_skill = ValueAlignmentSkill(llm)
        self.regret_skill = RegretRiskSkill(llm)
        self.future_skill = FutureSimulationSkill(llm)
        self.report_skill = ReportGenerateSkill(llm)
        self.current_agent = CurrentSelfAgent(llm)
        self.future_agent = FutureSelfAgent(llm)
        self.rational_agent = RationalMentorAgent(llm)
        self.emotion_agent = EmotionalSupportAgent(llm)

    def run(self, profile: dict, question: str) -> dict:
        if not question.strip():
            raise ValueError("决策问题不能为空")

        decomposition = self.decompose_skill.run(profile, question)
        options = self.option_skill.run(profile, question, decomposition)
        agent_views = {
            "current_self": self.current_agent.run(profile, question, decomposition, options),
            "future_self": self.future_agent.run(profile, question, decomposition, options),
            "rational_mentor": self.rational_agent.run(profile, question, decomposition, options),
            "emotional_supporter": self.emotion_agent.run(profile, question, decomposition, options),
        }
        alignment = self.alignment_skill.run(profile, decomposition, options)
        regret = self.regret_skill.run(profile, decomposition, options)
        future_sim = self.future_skill.run(profile, question, decomposition, options, agent_views)
        report = self.report_skill.run(profile, question, decomposition, options, alignment, regret, future_sim, agent_views)

        case_name = datetime.now().strftime("case_%Y%m%d_%H%M%S")
        result = {
            "case_name": case_name,
            "question": question,
            "decomposition": decomposition,
            "options": options,
            "agent_views": agent_views,
            "alignment": alignment,
            "regret": regret,
            "future_simulation": future_sim,
            "report": report,
        }
        save_case(result, case_name)
        report_path = REPORTS_DIR / f"{case_name}.md"
        report_path.write_text(report, encoding="utf-8")
        result["report_path"] = str(report_path)
        return result
