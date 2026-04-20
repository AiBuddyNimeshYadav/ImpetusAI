import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app.database import async_session
from backend.app.schemas.user import UserCreate
from backend.app.services.auth_service import signup

async def test():
    async with async_session() as db:
        try:
            user_data = UserCreate(email="error_search6@ex.com", password="password123", full_name="Ex", department="Engineering")
            user = await signup(db, user_data)
            print("User created:", user.id)
            await db.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
