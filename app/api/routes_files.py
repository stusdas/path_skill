from fastapi import APIRouter, UploadFile, File, Form
from controllers.file_ingestion_controller import FileIngestionController
from core.config import UPLOADS_DIR
import os, time

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
    mock: str = Form(default='true'),
):
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        path = UPLOADS_DIR / f.filename
        path.write_bytes(await f.read())
    return controller.ingest_uploaded_files(api_key=api_key, base_url=base_url, model=model, mock=(str(mock).lower() == 'true'))

