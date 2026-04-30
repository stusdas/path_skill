from core.chat_types import AnalysisState, MainMode, SubMode


class AnalysisStateMachine:
    STAGE_ORDERS = {
        'deep_understanding': [
            'problem_confirmation',
            'inner_tension_identification',
            'pattern_recognition',
            'deeper_trigger',
            'stage_summary',
        ],
        'self_opposition_view': [
            'voice_extraction',
            'voice_expansion',
            'protection_target',
            'cost_of_voice',
            'stage_summary',
        ],
        'decision_support': [
            'decision_definition',
            'inner_tension',
            'path_expansion',
            'stage_suggestion',
            'stage_summary',
        ],
        'multi_role_decision': [
            'role_frame_setup',
            'first_role_views',
            'role_divergence',
            'second_role_views',
            'stage_summary',
        ],
    }

    def initialize_if_needed(self, analysis_state: AnalysisState, main_mode: MainMode, sub_mode: SubMode, topic: str):
        if analysis_state.active:
            return analysis_state
        mapping = {
            ('deep_understanding', None): ('deep_understanding', 'problem_confirmation'),
            ('deep_understanding', 'self_opposition'): ('self_opposition_view', 'voice_extraction'),
            ('decision_support', None): ('decision_support', 'decision_definition'),
            ('decision_support', 'multi_role'): ('multi_role_decision', 'role_frame_setup'),
        }
        if (main_mode, sub_mode) in mapping:
            analysis_type, stage = mapping[(main_mode, sub_mode)]
            analysis_state.active = True
            analysis_state.analysis_type = analysis_type
            analysis_state.stage = stage
            analysis_state.stage_index = 1
            analysis_state.topic = topic
        return analysis_state

    def advance(self, analysis_state: AnalysisState):
        if not analysis_state.active or not analysis_state.analysis_type:
            return analysis_state
        order = self.STAGE_ORDERS.get(analysis_state.analysis_type, [])
        if analysis_state.stage in order:
            idx = order.index(analysis_state.stage)
            if idx < len(order) - 1:
                analysis_state.stage = order[idx + 1]
                analysis_state.stage_index = idx + 2
        return analysis_state

    def deactivate(self, analysis_state: AnalysisState):
        analysis_state.active = False
        analysis_state.analysis_type = None
        analysis_state.stage = None
        analysis_state.stage_index = 0
        analysis_state.topic = None
        analysis_state.waiting_for_user = False
        analysis_state.card_emitted = False
        analysis_state.slot_fill = {}
        return analysis_state
