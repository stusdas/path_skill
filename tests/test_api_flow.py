import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.main import app

client = TestClient(app)


def main():
    r = client.get('/health')
    assert r.status_code == 200

    r = client.get('/api/config/defaults')
    assert r.status_code == 200

    r = client.get('/showcase')
    assert r.status_code == 200

    r = client.post('/api/conversations/new', json={'title': 'E2E测试', 'conversation_type': 'standard'})
    assert r.status_code == 200
    cid = r.json()['id']

    r = client.post('/api/conversations/toggle-mode', json={
        'conversation_id': cid,
        'main_mode': 'decision_support',
        'sub_mode': 'multi_role',
    })
    assert r.status_code == 200

    r = client.post('/api/chat/send', json={
        'conversation_id': cid,
        'message': '请你根据我的资料，信息，帮我分析一下，我现阶段是考研还是找工作更好？',
        'api_key': '',
        'base_url': 'https://api.deepseek.com/v1',
        'model': 'deepseek-chat',
        'mock': True,
        'main_mode': 'decision_support',
        'sub_mode': 'multi_role',
    })
    assert r.status_code == 200
    data = r.json()
    assert data['conversation']['main_mode'] == 'decision_support'
    assert data['conversation']['sub_mode'] == 'multi_role'
    assert len(data['conversation']['messages']) >= 2

    files = {'files': ('manual_note.txt', '我最近在成长和稳定之间反复拉扯。', 'text/plain')}
    r = client.post('/api/upload-profile-files', files=files, data={
        'api_key': '',
        'base_url': 'https://api.deepseek.com/v1',
        'model': 'deepseek-chat',
        'mock': 'true',
    })
    assert r.status_code == 200
    out = r.json()
    assert '纳入对你的理解' in out['message']

    r = client.get('/api/memory')
    assert r.status_code == 200
    print('API_FLOW_OK')


if __name__ == '__main__':
    main()
