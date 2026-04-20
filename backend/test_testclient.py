import asyncio, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print('Testing rename directly with TestClient using existing user...')

res = client.post('/api/v1/auth/login', json={'email': 'test@impetus.com', 'password': 'Password123!'})
if res.status_code != 200:
    print(f'Login failed: {res.text}. Cannot test rename without conversations.')
    sys.exit(1)

token = res.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# Get conversations
res = client.get('/api/v1/chat/conversations', headers=headers)
convs = res.json()

if not convs:
    print('No conversations found for existing user. Aborting test.')
    sys.exit(1)

conv_id = convs[0]['id']
print(f'Trying to rename conv: {conv_id} from {convs[0]["title"]} to "TestClient Renamed"')

try:
    res = client.patch(f'/api/v1/chat/conversations/{conv_id}', headers=headers, json={'title': 'TestClient Renamed'})
    print(f'STATUS: {res.status_code}')
    print(f'RESPONSE: {res.text}')
    
    res = client.get(f'/api/v1/chat/conversations/{conv_id}', headers=headers)
    print(f'Final Title: {res.json().get("title")}')
except Exception as e:
    import traceback
    traceback.print_exc()
