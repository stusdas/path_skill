from fastapi import APIRouter, UploadFile, File, Form
from controllers.file_ingestion_controller import FileIngestionController
from core.config import UPLOADS_DIR

router = APIRouter()
controller = FileIngestionController()

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
