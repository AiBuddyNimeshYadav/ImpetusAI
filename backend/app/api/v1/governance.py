"""Governance API — handle access requests and role management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.access_request import AccessRequest
from app.schemas.governance import (
    AccessRequestCreate,
    AccessRequestProcess,
    AccessRequestResponse,
    GovernanceStats
)

router = APIRouter(prefix="/governance", tags=["Governance"])

@router.post("/request", response_model=AccessRequestResponse, status_code=201)
async def create_access_request(
    data: AccessRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a request for elevated access."""
    # Check for existing pending request
    existing = await db.execute(
        select(AccessRequest).where(
            AccessRequest.user_id == current_user.id,
            AccessRequest.status == "pending"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="You already have a pending access request."
        )

    req = AccessRequest(
        user_id=current_user.id,
        requested_role=data.requested_role,
        justification=data.justification
    )
    db.add(req)
    await db.flush()
    await db.refresh(req)
    
    # Eagerly load user for response
    result = await db.execute(
        select(AccessRequest)
        .options(selectinload(AccessRequest.user))
        .where(AccessRequest.id == req.id)
    )
    return result.scalar_one()

@router.get("/requests", response_model=list[AccessRequestResponse])
async def list_access_requests(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List access requests (Admin Only)."""
    if current_user.role not in ("admin", "hr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    query = select(AccessRequest).options(selectinload(AccessRequest.user)).order_by(AccessRequest.created_at.desc())
    if status_filter:
        query = query.where(AccessRequest.status == status_filter)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/requests/{request_id}/process", response_model=AccessRequestResponse)
async def process_access_request(
    request_id: str,
    data: AccessRequestProcess,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject an access request (Admin Only)."""
    if current_user.role not in ("admin", "hr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(AccessRequest)
        .options(selectinload(AccessRequest.user))
        .where(AccessRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request has already been processed")

    req.status = data.status
    req.admin_comment = data.admin_comment
    req.processed_by = current_user.id

    if data.status == "approved":
        # Apply the role change
        req.user.role = req.requested_role

    await db.flush()
    await db.refresh(req)
    return req

@router.get("/stats", response_model=GovernanceStats)
async def get_governance_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get high-level statistics for the workplace platform (Admin Only)."""
    if current_user.role not in ("admin", "hr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    total_reqs = await db.execute(select(func.count(AccessRequest.id)))
    pending_reqs = await db.execute(select(func.count(AccessRequest.id)).where(AccessRequest.status == "pending"))
    total_users = await db.execute(select(func.count(User.id)))
    active_users = await db.execute(select(func.count(User.id)).where(User.is_active == True))

    return {
        "total_requests": total_reqs.scalar(),
        "pending_requests": pending_reqs.scalar(),
        "total_users": total_users.scalar(),
        "active_users": active_users.scalar()
    }
