"""Admin API — user management (admin only)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import AdminUserCreate, AdminUserResponse, AdminUserUpdate
from app.services.auth_service import hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AdminUserResponse]:
    """List all platform users. Admin only."""
    _require_admin(current_user)
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [AdminUserResponse.model_validate(u) for u in result.scalars().all()]


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: str,
    data: AdminUserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    """Update a user's role and/or registration_status. Admin only."""
    _require_admin(current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role is not None:
        user.role = data.role
    if data.registration_status is not None:
        user.registration_status = data.registration_status
        # Keep is_active in sync — deps.py guards on user.is_active for every request
        user.is_active = data.registration_status == "active"
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.flush()
    await db.refresh(user)
    return AdminUserResponse.model_validate(user)


@router.post("/users", response_model=AdminUserResponse, status_code=201)
async def create_user(
    data: AdminUserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    """Create a user directly (bypasses signup flow). Admin only."""
    _require_admin(current_user)
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        department=data.department,
        role=data.role,
        employee_id=data.employee_id,
        registration_status="active",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return AdminUserResponse.model_validate(user)
