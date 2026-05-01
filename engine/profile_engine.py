from memory.profile_store import save_profile
from skills.profile_distill_skill import ProfileDistillSkill


class ProfileEngine:
    def __init__(self, llm):
        self.skill = ProfileDistillSkill(llm)

    def run(self, file_items: list, manual_input: dict) -> dict:
        """Original blocking version (kept for backward compat)."""
        for _step, _label, final in self.run_with_progress(file_items, manual_input):
            pass
        return final

    def run_with_progress(self, file_items: list, manual_input: dict):
        """Generator that yields (step_index, label, partial_result) at each stage."""
        if not file_items and not any(str(v).strip() for v in manual_input.values()):
            raise ValueError("至少提供资料文件或手动信息")

        evidence_list = []
        for i, item in enumerate(file_items):
            yield (1, "正在对人物进行蒸馏：从上传的原始资料中提取有效信息…", None)
            evidence = self.skill.run_file_evidence_extract(item)
            if evidence:
                evidence_list.append({
                    "file_name": item["file_name"],
                    "file_type": item["file_type"],
                    "source_path": item["source_path"],
                    **evidence,
                })

        modules = {}

        yield (2, "正在对人物进行蒸馏：生成基础人物摘要…", None)
        modules["human_info_card"] = self.skill.run_info_card(manual_input, evidence_list)

        yield (3, "正在对人物进行蒸馏：分析说话风格与表达习惯…", None)
        modules["expression_style"] = self.skill.run_expression_style(manual_input, evidence_list)

        yield (4, "正在对人物进行蒸馏：提取自我定义与重要记忆…", None)
        modules["self_memory"] = self.skill.run_self_memory(manual_input, evidence_list)

        yield (5, "正在对人物进行蒸馏：分析行为模式与决策习惯…", None)
        modules["behavior_patterns"] = self.skill.run_behavior_pattern(manual_input, evidence_list)

        yield (6, "正在对人物进行蒸馏：分析隐含信念与底层规则…", None)
        modules["implicit_beliefs"] = self.skill.run_implicit_beliefs(manual_input, evidence_list)

        yield (7, "正在对人物进行蒸馏：构建四层运行系统…", None)
        modules["four_layer_system"] = self.skill.run_four_layer_system(manual_input, evidence_list, modules)

        yield (8, "正在对人物进行蒸馏：融合各维度信息，生成完整人物画像…", None)
        final_profile = self.skill.run_profile_fusion(manual_input, modules)
        final_profile["evidence_index"] = evidence_list
        final_profile["module_outputs"] = modules
        save_profile(final_profile)

        yield (9, "画像生成完成！", final_profile)

