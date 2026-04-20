"""
ImpetusAI Workplace Platform — FastAPI Application Entry Point.

Run with: uvicorn app.main:app --reload --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db

settings = get_settings()

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("impetusai")


# ── Startup / Shutdown ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle: init DB, seed demo data."""
    logger.info("🚀 Starting ImpetusAI Backend …")

    # 0. Reset LLM gateway singleton so it picks up current .env settings
    import ai.llm.gateway as _gw
    _gw._gateway = None
    logger.info(f"🤖 LLM: {settings.LLM_PROVIDER}/{settings.LLM_MODEL}")

    # 1. Create DB tables
    await init_db()
    logger.info("✅ Database tables created")

    # 2. Seed demo HR policies into ChromaDB
    demo_dir = os.path.join(os.path.dirname(__file__), "..", "demo_policies")
    demo_dir = os.path.abspath(demo_dir)
    if os.path.isdir(demo_dir):
        from ai.rag.retriever import get_rag_service
        rag = get_rag_service()
        collection = rag.get_collection("hr_policies")
        if collection.count() == 0:
            count = rag.ingest_demo_policies(demo_dir)
            logger.info(f"📄 Seeded {count} demo policy chunks into ChromaDB")
        else:
            logger.info(f"📄 ChromaDB already has {collection.count()} chunks — skipping seed")

    # 3. Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 4. Bootstrap admin user if none exists
    from app.database import async_session
    from app.models.user import User
    from app.services.auth_service import hash_password
    from sqlalchemy import func, select
    from sqlalchemy.exc import IntegrityError

    async with async_session() as db:
        count = (await db.execute(select(func.count(User.id)).where(User.role == "admin"))).scalar()
        if count == 0:
            try:
                admin = User(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    full_name="System Administrator",
                    department="IT",
                    role="admin",
                    registration_status="active",
                    is_active=True,
                )
                db.add(admin)
                await db.commit()
                logger.info(f"Bootstrap admin created: {settings.ADMIN_EMAIL}")
            except IntegrityError:
                await db.rollback()
                logger.info("Admin bootstrap skipped — already exists")
        else:
            logger.info("Admin user already exists — skipping bootstrap")

    # 5. Seed IT team members
    from app.services.it_team import IT_TEAM_MEMBERS
    async with async_session() as db:
        seeded = 0
        for member in IT_TEAM_MEMBERS:
            existing = (await db.execute(select(User).where(User.email == member["email"]))).scalar_one_or_none()
            if not existing:
                db.add(User(
                    email=member["email"],
                    hashed_password=hash_password(member["password"]),
                    full_name=member["full_name"],
                    employee_id=member["employee_id"],
                    department=member["department"],
                    role=member["role"],
                    registration_status="active",
                    is_active=True,
                ))
                seeded += 1
        if seeded:
            await db.commit()
            logger.info(f"👥 Seeded {seeded} IT team members")
        else:
            logger.info("👥 IT team already seeded — skipping")

    # 6. Seed initial leave balances for all non-IT users (2026 allocations)
    from app.models.leave_balance import LeaveBalance
    from ai.agents.leave_data import DEFAULT_ANNUAL_ALLOCATION
    import datetime as _dt
    CURRENT_YEAR = _dt.date.today().year
    async with async_session() as db:
        # Get all regular (non-IT-agent) users
        all_users = (await db.execute(
            select(User).where(User.is_active == True, User.role.notin_(["it_agent"]))
        )).scalars().all()
        seeded_bal = 0
        for u in all_users:
            for lt, total in DEFAULT_ANNUAL_ALLOCATION.items():
                existing = (await db.execute(
                    select(LeaveBalance).where(
                        LeaveBalance.user_id == u.id,
                        LeaveBalance.leave_type == lt,
                        LeaveBalance.year == CURRENT_YEAR,
                    )
                )).scalar_one_or_none()
                if not existing:
                    db.add(LeaveBalance(
                        user_id=u.id,
                        leave_type=lt,
                        year=CURRENT_YEAR,
                        total_allocated=total,
                        used=0,
                    ))
                    seeded_bal += 1
        if seeded_bal:
            await db.commit()
            logger.info(f"📅 Seeded {seeded_bal} leave balance records")
        else:
            logger.info("📅 Leave balances already seeded — skipping")

    logger.info("✅ ImpetusAI Backend ready!")
    yield
    logger.info("👋 Shutting down ImpetusAI Backend")


# ── FastAPI App ─────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered IT Service Desk & HR Assistant platform",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────
from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from app.api.v1.governance import router as governance_router
from app.api.v1.tickets import router as tickets_router
from app.api.v1.leave import router as leave_router
from app.api.v1.timesheet import router as timesheet_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(governance_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(leave_router, prefix="/api/v1")
app.include_router(timesheet_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
