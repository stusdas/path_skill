from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from controllers.file_ingestion_controller import FileIngestionController
from core.config import UPLOADS_DIR, STATIC_PROFILE_PATH
from core.llm_client import LLMClient
from core.utils import dump_json
from engine.profile_engine import ProfileEngine
from parsers.file_router import scan_folder
import os, time, json

router = APIRouter()
controller = FileIngestionController()

@router.get('/files')
def list_files():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for name in os.listdir(UPLOADS_DIR):
        fp = UPLOADS_DIR / name
        if fp.is_file():
            stat = fp.stat()
            items.append({
                'name': name,
                'size': stat.st_size,
                'uploaded_at': time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime)),
            })
    return {'files': items}

@router.delete('/files/{filename}')
def delete_file(filename: str):
    fp = UPLOADS_DIR / filename
    if fp.exists():
        fp.unlink()
    return {'ok': True}

@router.post('/upload-profile-files')
async def upload_profile_files(
    files: list[UploadFile] = File(...),
    api_key: str = Form(default=''),
    base_url: str = Form(default='https://api.deepseek.com/v1'),
    model: str = Form(default='deepseek-chat'),
    mock: str = Form(default='false'),
):
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        path = UPLOADS_DIR / f.filename
        path.write_bytes(await f.read())

    def generate():
        llm = LLMClient(api_key=api_key, base_url=base_url, model=model, mock=(str(mock).lower() == 'true'))
        engine = ProfileEngine(llm)
        file_items = scan_folder(str(UPLOADS_DIR))
        manual_input = {'nickname': '未填写', 'occupation': '', 'mbti': '', 'zodiac': '', 'attachment_style': '', 'labels': '', 'impression': ''}
        try:
            for step, label, result in engine.run_with_progress(file_items, manual_input):
                yield json.dumps({"type": "progress", "step": step, "label": label}, ensure_ascii=False) + "\n"
            yield json.dumps({"type": "done", "message": "画像生成完成！"}, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False) + "\n"

    return StreamingResponse(generate(), media_type="text/plain")
