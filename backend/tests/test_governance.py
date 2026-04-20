import httpx
import asyncio
import json

BASE_URL = "http://localhost:8001/api/v1"

async def test_governance_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login as a regular user (create one if needed via signup)
        # Assuming test_user exists from previous tasks or we create it
        signup_data = {
            "email": "gov_test@impetus.com",
            "password": "Password123!",
            "full_name": "Governance Test User"
        }
        await client.post(f"{BASE_URL}/auth/signup", json=signup_data)
        
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "gov_test@impetus.com",
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("1. User logged in.")

        # 2. Submit access request
        req_data = {
            "requested_role": "hr_admin",
            "justification": "I need to manage leave policies for my department as a new lead."
        }
        req_res = await client.post(f"{BASE_URL}/governance/request", json=req_data, headers=headers)
        request_id = req_res.json()["id"]
        print(f"2. Access request submitted. ID: {request_id}")

        # 3. Check stats (Should fail as regular user)
        stats_res = await client.get(f"{BASE_URL}/governance/stats", headers=headers)
        print(f"3. Stats check (Regular User): {stats_res.status_code} (Expected 403)")

        # 4. Login as Admin (Assuming admin@impetus.com exists or we use the seed script logic)
        # For this test, let's assume 'test@impetus.com' is admin (as we previously set it)
        admin_login = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "test@impetus.com",
            "password": "Test1234!"
        })
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("4. Admin logged in.")

        # 5. List requests
        list_res = await client.get(f"{BASE_URL}/governance/requests", headers=admin_headers)
        print(f"5. Admin listed requests. Count: {len(list_res.json())}")

        # 6. Approve request
        process_data = {
            "status": "approved",
            "admin_comment": "Approved based on department lead verification."
        }
        approve_res = await client.post(f"{BASE_URL}/governance/requests/{request_id}/process", json=process_data, headers=admin_headers)
        print(f"6. Request approved. New user role: {approve_res.json()['user']['role']}")

        # 7. Verify user role updated
        me_res = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"7. User role verified via /me: {me_res.json()['role']}")

if __name__ == "__main__":
    asyncio.run(test_governance_flow())
