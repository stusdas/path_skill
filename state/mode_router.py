from core.chat_types import MainMode, SubMode, AnalysisState


class ModeRouter:
    def route(self, main_mode: MainMode, sub_mode: SubMode, analysis_state: AnalysisState, message_text: str):
        suggest_deeper = False
        if main_mode == 'normal':
            keywords = ['考研', '找工作', '该不该', '要不要', '纠结', '选择', 'offer', '换工作', '读研']
            suggest_deeper = any(k in message_text for k in keywords)
        return {
            'main_mode': main_mode,
            'sub_mode': sub_mode,
            'suggest_deeper': suggest_deeper,
            'analysis_active': analysis_state.active,
        }
