from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, PlainTextResponse
from app.api.routes_chat import router as chat_router
from app.api.routes_memory import router as memory_router
from app.api.routes_files import router as files_router
from app.api.routes_settings import router as settings_router
from core.config import APP_DIR, ROOT_DIR

app = FastAPI(title='LifePath Chat Upgrade', version='0.2.0-enhanced')
app.include_router(chat_router, prefix='/api')
app.include_router(memory_router, prefix='/api')
app.include_router(files_router, prefix='/api')
app.include_router(settings_router, prefix='/api')

frontend_dir = APP_DIR / 'frontend'
app.mount('/static', StaticFiles(directory=str(frontend_dir)), name='static')

@app.get('/')
def root():
    return RedirectResponse(url='/static/index.html')

@app.get('/showcase')
def showcase():
    return FileResponse(str(frontend_dir / 'showcase.html'))

@app.get('/static/showcase.html')
def showcase_static_fallback():
    return FileResponse(str(frontend_dir / 'showcase.html'))

@app.get('/demo-script')
def demo_script():
    path = ROOT_DIR / 'docs' / 'demo_script.md'
    return PlainTextResponse(path.read_text(encoding='utf-8'))

@app.get('/health')
def health():
    return {'status': 'ok'}
