from core.llm_client import LLMClient
from core.utils import dump_json, now_iso
from core.config import UPLOADS_DIR, STATIC_PROFILE_PATH
from parsers.file_router import scan_folder
from engine.profile_engine import ProfileEngine
from memory.user_memory_store import load_user_memory


class FileIngestionController:
    def ingest_uploaded_files(self, api_key: str = '', base_url: str = '', model: str = '', mock: bool = True):
        llm = LLMClient(api_key=api_key, base_url=base_url, model=model, mock=mock)
        file_items = scan_folder(str(UPLOADS_DIR))
        profile_engine = ProfileEngine(llm)
        profile = profile_engine.run(file_items, {
            'nickname': '未填写',
            'occupation': '',
            'mbti': '',
            'zodiac': '',
            'attachment_style': '',
            'labels': [],
            'impression': '',
        })
        dump_json(STATIC_PROFILE_PATH, profile)
        return {
            'message': '我已经把这份资料里的关键内容纳入对你的理解，主要补充了你的经历、表达方式和长期关注点。',
            'memory': load_user_memory().model_dump(),
            'profile_summary': profile.get('executive_summary', '已重建画像'),
            'updated_at': now_iso(),
        }
