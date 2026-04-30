import json
from typing import Dict, List

from core.prompt_loader import load_prompt
from core.utils import ensure_json, truncate_text
from skills.skill_base import SkillBase


class ProfileDistillSkill(SkillBase):
    def run_file_evidence_extract(self, file_item: Dict) -> Dict:
        system_prompt = load_prompt("profile/file_evidence_extract.md")
        user_prompt = f"文件元信息：{json.dumps({k: v for k, v in file_item.items() if k != 'content'}, ensure_ascii=False)}\n\n文件内容：\n{truncate_text(file_item['content'], 8000)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.2))

    def run_info_card(self, manual_input: Dict, evidence_list: List[Dict]) -> Dict:
        system_prompt = load_prompt("profile/info_card.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.2))

    def run_expression_style(self, manual_input: Dict, evidence_list: List[Dict]) -> Dict:
        system_prompt = load_prompt("profile/expression_style.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.2))

    def run_self_memory(self, manual_input: Dict, evidence_list: List[Dict]) -> Dict:
        system_prompt = load_prompt("profile/self_memory.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.25))

    def run_behavior_pattern(self, manual_input: Dict, evidence_list: List[Dict]) -> Dict:
        system_prompt = load_prompt("profile/behavior_pattern.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.25))

    def run_implicit_beliefs(self, manual_input: Dict, evidence_list: List[Dict]) -> Dict:
        system_prompt = load_prompt("profile/implicit_beliefs.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.25))

    def run_four_layer_system(self, manual_input: Dict, evidence_list: List[Dict], modules: Dict) -> Dict:
        system_prompt = load_prompt("profile/four_layer_system.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n证据摘要：\n{json.dumps(evidence_list, ensure_ascii=False, indent=2)}\n\n已有模块输出：\n{json.dumps(modules, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.25))

    def run_profile_fusion(self, manual_input: Dict, modules: Dict) -> Dict:
        system_prompt = load_prompt("profile/profile_fusion.md")
        user_prompt = f"手动信息：\n{json.dumps(manual_input, ensure_ascii=False, indent=2)}\n\n模块输出：\n{json.dumps(modules, ensure_ascii=False, indent=2)}"
        return ensure_json(self.llm.complete(system_prompt, user_prompt, temperature=0.2))
