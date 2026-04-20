import asyncio, httpx

async def test_api():
    base_url = 'http://localhost:8000/api/v1'
    async with httpx.AsyncClient() as client:
        print('Logging in...')
        res = await client.post(f'{base_url}/auth/login', json={'email': 'test@impetus.com', 'password': 'Password123!'})
        if res.status_code != 200:
            print(f'Login failed: {res.text}. Trying signup...')
            res = await client.post(f'{base_url}/auth/signup', json={'email': 'test@impetus.com', 'password': 'Password123!', 'full_name': 'Test User'})
            print(f'Signup status: {res.status_code}')
            res = await client.post(f'{base_url}/auth/login', json={'email': 'test@impetus.com', 'password': 'Password123!'})
            
        if res.status_code != 200:
            print('Could not login or signup.')
            return
            
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        print('Getting conversations...')
        res = await client.get(f'{base_url}/chat/conversations', headers=headers)
        convs = res.json()
        
        if not convs:
            print('No conversations found. Creating one...')
            res = await client.post(f'{base_url}/chat/send', headers=headers, json={"message": "Hello intent", "conversation_id": None})
            print(f'Create conv status: {res.status_code}')
            res = await client.get(f'{base_url}/chat/conversations', headers=headers)
            convs = res.json()
            
        target = convs[0]
        print(f'Target Conv: {target["id"]} | Current Title: {target["title"]}')
        
        new_title = 'Renamed title via API'
        print(f'Sending PATCH to rename to: {new_title}')
        res = await client.patch(f'{base_url}/chat/conversations/{target["id"]}', headers=headers, json={'title': new_title})
        print(f'PATCH status: {res.status_code} | response: {res.text}')
        
        print('Verifying rename...')
        res = await client.get(f'{base_url}/chat/conversations/{target["id"]}', headers=headers)
        print(f'GET verified title: {res.json().get("title")}')

if __name__ == '__main__':
    asyncio.run(test_api())
