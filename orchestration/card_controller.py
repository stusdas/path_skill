from core.chat_types import AnalysisState


class CardController:
    def maybe_emit(self, analysis_state: AnalysisState, analysis_pack: dict | None = None):
        if not analysis_state.active or analysis_state.card_emitted:
            return None
        if analysis_state.stage != 'stage_summary':
            return None
        analysis_state.card_emitted = True

        if analysis_state.analysis_type == 'deep_understanding':
            items = [
                '当前问题已从表面选择转到更深的自我定位与内在拉扯。',
                '系统已识别用户在成长与安全感之间的核心矛盾。',
                '下一步更适合继续追问：用户到底害怕选错路，还是害怕选错后会否定自己。',
            ]
            return {'type': 'understanding_card', 'title': '阶段性理解', 'items': items}

        if analysis_state.analysis_type == 'self_opposition_view':
            items = [
                '已识别内在反对声音的核心句式。',
                '已识别它更像在保护用户免于再次经历失败或自我怀疑。',
                '已识别它的代价：持续把用户拉回更保守但未必更适合的路径。',
            ]
            return {'type': 'inner_conflict_card', 'title': '内部冲突卡', 'items': items}

        if analysis_pack and analysis_state.analysis_type == 'decision_support':
            opts = analysis_pack.get('options', {}).get('options', [])
            first = opts[0]['name'] if opts else '路径 A'
            second = opts[1]['name'] if len(opts) > 1 else '路径 B'
            keyq = analysis_pack.get('decomposition', {}).get('deep_choice') or analysis_pack.get('decomposition', {}).get('hidden_conflicts', ['当前更关键的问题尚待确认'])[0]
            return {
                'type': 'path_compare_card',
                'title': '路径对比卡',
                'items': [
                    f'已比较：{first} 与 {second}',
                    f'当前更关键的问题：{keyq}',
                    '建议继续确认：用户此刻的倾向是价值选择，还是压力选择。',
                ],
            }

        if analysis_pack and analysis_state.analysis_type == 'multi_role_decision':
            views = analysis_pack.get('agent_views', {})
            items = []
            for k in ['current_self', 'future_self', 'rational_mentor', 'emotional_supporter']:
                if k in views:
                    label = {
                        'current_self': '当前的你',
                        'future_self': '未来的你',
                        'rational_mentor': '理性导师',
                        'emotional_supporter': '情绪支持者',
                    }[k]
                    items.append(f"{label}：{views[k].get('core_concern', views[k].get('preferred_option', '已生成观点'))}")
            if not items:
                items = ['已出现多个角色视角', '已识别主要分歧点', '下一步适合继续做多视角整合']
            return {'type': 'role_view_card', 'title': '多角色视角卡', 'items': items[:4]}

        return None
