import json
import asyncio
import httpx
import requests
from core.chat_types import AppSettings
from core.config import API_CONFIG_PATH, DEFAULT_BASE_URL, DEFAULT_MODEL
from core.utils import load_json


class LLMClient:
    def __init__(self, api_key: str = '', base_url: str = '', model: str = '', mock: bool = False):
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.model = model or DEFAULT_MODEL
        self.mock = mock

    @classmethod
    def from_saved_settings(cls):
        cfg = load_json(API_CONFIG_PATH, default={}) or {}
        settings = AppSettings(**cfg)
        return cls(settings.api_key, settings.base_url, settings.model, settings.mock_mode)

    async def async_complete_stream(self, system_prompt: str, user_prompt: str, temperature: float = 0.3):
        if self.mock:
            async for chunk in self._mock_stream(system_prompt, user_prompt):
                yield chunk
            return

        if not self.api_key:
            raise ValueError('请先提供 API Key，或打开 Mock 模式')

        url = self.base_url.rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'temperature': temperature,
            'stream': True,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        content = data['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def _mock_stream(self, system_prompt: str, user_prompt: str):
        full_text = self._mock_response(system_prompt, user_prompt)
        # Split into small chunks to simulate typing
        chunk_size = 3
        for i in range(0, len(full_text), chunk_size):
            yield full_text[i:i+chunk_size]
            await asyncio.sleep(0.02)


    def _mock_response(self, system_prompt: str, user_prompt: str) -> str:
        sp = system_prompt.lower()
        up = user_prompt[:1500]
        # profile / decision mocks retained from old project
        if 'file evidence extractor' in sp:
            return json.dumps({'file_summary': '该文件包含用户自述与成长/稳定冲突线索。', 'identity_clues': ['长期主义'], 'style_clues': ['结构化表达'], 'events': ['面临关键选择'], 'evidence_quotes': ['我怕选错路']}, ensure_ascii=False)
        if 'information card extractor' in sp:
            return json.dumps({'nickname': '未填写', 'occupation': '学生/青年探索期', 'mbti': '原材料不足', 'zodiac': '原材料不足', 'attachment_style': '原材料不足', 'labels': ['重视成长', '纠结型'], 'impression': '结构化、自省、长期主义', 'conflicts_with_manual_input': []}, ensure_ascii=False)
        if 'expression style analyst' in sp:
            return json.dumps({'high_frequency_terms': ['长期', '成长'], 'catchphrases': ['我觉得', '其实吧'], 'sentence_style': '结构化长句', 'tone_words': ['其实', '就是', '比如'], 'emoji_style': '较少使用', 'punctuation_habits': '常用分段与冒号', 'message_density': '高', 'formality_level': 3, 'communication_mode': '更像在梳理自己', 'style_to_thinking_bridge': '语言风格显示其偏抽象总结与系统思考', 'evidence_quotes': ['我现在的想法是']}, ensure_ascii=False)
        if 'self memory analyst' in sp:
            return json.dumps({'work_view': '重视成长与长期发展', 'money_view': '重要但非唯一标准', 'relationship_view': '关系应服务于共同成长', 'growth_view': '明显偏长期主义', 'life_habits': {'routine': '原材料不足'}, 'key_events': ['关键人生选择阶段'], 'growth_trajectory': '自我反思增强', 'evidence_quotes': ['人生局部最优解']}, ensure_ascii=False)
        if 'behavior pattern analyst' in sp:
            return json.dumps({'stress_response': '压力下倾向加倍分析', 'conflict_pattern': '更想看清问题根源', 'repair_pattern': '通过重新梳理恢复控制感', 'decision_pattern': '在重要决策上容易过度权衡', 'recovery_pattern': '通过对话与结构化分析恢复清晰感', 'evidence_quotes': ['我希望你认真思考']}, ensure_ascii=False)
        if 'implicit beliefs analyst' in sp:
            return json.dumps({'core_needs': ['做对长期选择', '减少后悔'], 'hidden_beliefs': ['错误选择会在未来放大成本'], 'fear_scripts': ['怕选错导致长期后悔'], 'contradictions': ['想尽快前进又想把决定想透'], 'evidence_quotes': ['尽量去避免这些问题']}, ensure_ascii=False)
        if 'four-layer human operating system analyst' in sp:
            return json.dumps({'input_layer': {'value_filter': ['成长', '长期收益']}, 'interpretation_layer': {'cognitive_model': '系统思维'}, 'reaction_layer': {'under_pressure': '深度分析'}, 'implicit_rules_layer': {'core_script': '通过看清自己来减少后悔'}, 'evidence_quotes': ['不是分析人，而是还原一个人的运行系统']}, ensure_ascii=False)
        if 'profile fusion architect' in sp:
            return json.dumps({'human_info_card': {'nickname': '未填写', 'occupation': '学生/青年探索期', 'labels': ['长期主义', '纠结型']}, 'expression_style': {'sentence_style': '结构化长句'}, 'self_memory': {'work_view': '重视长期成长'}, 'behavior_patterns': {'decision_pattern': '纠结但认真'}, 'implicit_beliefs': {'core_needs': ['减少后悔']}, 'four_layer_system': {'input_layer': {'value_filter': ['成长']}}, 'executive_summary': '高度自省、长期主义、在重大选择上容易过度权衡。', 'evidence_quotes': ['人生局部最优解']}, ensure_ascii=False)
        if 'decision decomposition strategist' in sp:
            return json.dumps({'decision_goal': '做出更符合长期发展的选择', 'problem_type': '职业/人生重大选择', 'options': ['考研', '找工作', '过渡路径'], 'dimensions': ['短期收益', '长期成长', '后悔风险'], 'hidden_conflicts': ['安全感与成长欲的冲突'], 'missing_information': ['资源缓冲期']}, ensure_ascii=False)
        if 'option generation strategist' in sp:
            return json.dumps({'options': [{'name': '考研路径', 'type': 'direct', 'description': '继续投入准备期', 'when_fit': ['明确想争更高平台'], 'risks': ['不确定性高']}, {'name': '工作路径', 'type': 'direct', 'description': '先进入真实环境积累经验', 'when_fit': ['需要验证方向'], 'risks': ['可能过早锁定路径']}, {'name': '过渡路径', 'type': 'bridge', 'description': '保留成长空间并降低短期风险', 'when_fit': ['既不想停滞又不想莽撞'], 'risks': ['执行要求高']} ]}, ensure_ascii=False)
        if 'value alignment analyst' in sp:
            return json.dumps({'alignment_scores': [{'option': '考研路径', 'score': 76}, {'option': '工作路径', 'score': 72}, {'option': '过渡路径', 'score': 88}], 'system_level_explanation': '过渡路径更适合连接长期价值与现实承受度。'}, ensure_ascii=False)
        if 'regret risk analyst' in sp:
            return json.dumps({'regret_analysis': [{'option': '考研路径', 'long_term_regret_risk': '中'}, {'option': '工作路径', 'long_term_regret_risk': '中高'}, {'option': '过渡路径', 'long_term_regret_risk': '低'}], 'system_risk_note': '更容易后悔没有给长期成长机会的选择。'}, ensure_ascii=False)
        if 'future simulation synthesizer' in sp:
            return json.dumps({'future_view_summary': [{'horizon': '1年后', 'likely_reflection': '希望更清楚方向'}, {'horizon': '3年后', 'likely_reflection': '更看重是否积累了可迁移能力'}], 'core_future_warning': '警惕为了缓解眼前焦虑而锁死长期空间。'}, ensure_ascii=False)
        if 'final decision report writer' in sp:
            return '# 决策建议报告\n\n核心结论：更适合选择带缓冲的过渡路径。'

        # chat mode mocks
        if '普通聊天模式' in system_prompt:
            return '这个问题对你来说，可能已经不只是“考研还是工作”这么简单了。我先不急着替你下判断。你现在更纠结的是未来发展、现实压力，还是你还没想清自己到底更想要哪种生活状态？'
        if '深度理解模式下的“自我对立视角”' in system_prompt:
            return '我先不急着替你选考研还是工作。这次我想试着把你心里那个总会把你拉回去的声音单独拿出来看看。它可能不是在故意阻碍你，而是在用一种很熟悉的方式保护你。'
        if '深度理解模式' in system_prompt:
            return '我先不急着回答你“考研还是工作”哪个更好。对你来说，这个问题很可能不只是路径选择，而是在问：我现在到底该继续准备自己，还是该正式进入社会验证自己。'
        if '决策辅助模式下的“多角色聊天”' in system_prompt:
            return '我先用几个不同视角陪你看：当前的你、未来的你、理性导师、情绪支持者。我们先看，它们最不一致的地方在哪里。'
        if '决策辅助模式' in system_prompt:
            return '我先不急着给你结论。对你来说，这个问题表面上是在选“考研还是工作”，更深一层其实是在选继续投入一个更长期的准备期，还是先进入现实环境里积累经验。'

        return f'【Mock回复】我已收到你的问题：{up[:120]}'
