from memory.profile_store import save_profile
from skills.profile_distill_skill import ProfileDistillSkill


class ProfileEngine:
    def __init__(self, llm):
        self.skill = ProfileDistillSkill(llm)

    def run(self, file_items: list, manual_input: dict) -> dict:
        if not file_items and not any(str(v).strip() for v in manual_input.values()):
            raise ValueError("至少提供资料文件或手动信息")

        evidence_list = []
        for item in file_items:
            evidence = self.skill.run_file_evidence_extract(item)
            if evidence:
                evidence_list.append({
                    "file_name": item["file_name"],
                    "file_type": item["file_type"],
                    "source_path": item["source_path"],
                    **evidence,
                })

        modules = {}
        modules["human_info_card"] = self.skill.run_info_card(manual_input, evidence_list)
        modules["expression_style"] = self.skill.run_expression_style(manual_input, evidence_list)
        modules["self_memory"] = self.skill.run_self_memory(manual_input, evidence_list)
        modules["behavior_patterns"] = self.skill.run_behavior_pattern(manual_input, evidence_list)
        modules["implicit_beliefs"] = self.skill.run_implicit_beliefs(manual_input, evidence_list)
        modules["four_layer_system"] = self.skill.run_four_layer_system(manual_input, evidence_list, modules)

        final_profile = self.skill.run_profile_fusion(manual_input, modules)
        final_profile["evidence_index"] = evidence_list
        final_profile["module_outputs"] = modules
        save_profile(final_profile)
        return final_profile
