"""Leave API — create, list, and manage leave requests."""

import datetime as _dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.models.user import User
from app.models.leave_request import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.api.deps import get_current_user
from app.schemas.leave import LeaveBalanceResponse, LeaveRequestCreate, LeaveRequestResponse, LeaveRequestUpdate
from ai.agents.leave_data import DEFAULT_ANNUAL_ALLOCATION

router = APIRouter(prefix="/leave", tags=["Leave"])


def _leave_reference(leave_id: str) -> str:
    return f"LV-{leave_id[:8].upper()}"


async def _get_or_seed_balances(user_id: str, db: AsyncSession) -> dict[str, LeaveBalance]:
    """Load LeaveBalance rows for current year, seeding if missing."""
    year = _dt.date.today().year
    result = await db.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
    )
    rows = {b.leave_type: b for b in result.scalars().all()}
    if not rows:
        for lt, total in DEFAULT_ANNUAL_ALLOCATION.items():
            db.add(LeaveBalance(user_id=user_id, leave_type=lt, year=year, total_allocated=total, used=0))
        await db.flush()
        result2 = await db.execute(
            select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
        )
        rows = {b.leave_type: b for b in result2.scalars().all()}
    return rows


@router.get("/balance", response_model=LeaveBalanceResponse)
async def get_leave_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current leave balance for the logged-in user from LeaveBalance table."""
    rows = await _get_or_seed_balances(current_user.id, db)
    balance = {lt: max(0, b.total_allocated - b.used) for lt, b in rows.items()}
    for lt, total in DEFAULT_ANNUAL_ALLOCATION.items():
        balance.setdefault(lt, total)
    return LeaveBalanceResponse(**balance)


@router.post("", response_model=LeaveRequestResponse, status_code=201)
async def create_leave_request(
    data: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new leave request and deduct from LeaveBalance."""
    rows = await _get_or_seed_balances(current_user.id, db)
    bal = rows.get(data.leave_type)
    available = max(0, bal.total_allocated - bal.used) if bal else 0
    if available < data.days:
        raise HTTPException(status_code=400, detail=f"Insufficient {data.leave_type} balance ({available} days available)")

    leave = LeaveRequest(
        user_id=current_user.id,
        conversation_id=data.conversation_id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        days=data.days,
        reason=data.reason,
        status="pending",
    )
    db.add(leave)
    await db.flush()
    leave.reference = _leave_reference(leave.id)

    # Deduct balance
    if bal:
        bal.used = bal.used + data.days

    await db.flush()
    await db.refresh(leave)
    return LeaveRequestResponse.model_validate(leave)


@router.get("", response_model=list[LeaveRequestResponse])
async def list_leave_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all leave requests for the current user (or all if admin/hr_admin)."""
    query = select(LeaveRequest).order_by(LeaveRequest.created_at.desc())
    if current_user.role == "employee":
        query = query.where(LeaveRequest.user_id == current_user.id)
    result = await db.execute(query)
    return [LeaveRequestResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/{leave_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    leave_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single leave request."""
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if current_user.role == "employee" and leave.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return LeaveRequestResponse.model_validate(leave)


@router.patch("/{leave_id}", response_model=LeaveRequestResponse)
async def update_leave_request(
    leave_id: str,
    data: LeaveRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update leave status. Restores balance on cancellation or rejection."""
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if current_user.role == "employee":
        if leave.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if data.status and data.status != "cancelled":
            raise HTTPException(status_code=403, detail="Employees can only cancel their own requests")
        if leave.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending requests can be cancelled")

    prev_status = leave.status
    if data.status:
        leave.status = data.status
        if data.status in ("approved", "rejected"):
            leave.approved_by = current_user.id

        # Restore balance if moving from pending → cancelled or rejected
        if prev_status == "pending" and data.status in ("cancelled", "rejected"):
            rows = await _get_or_seed_balances(leave.user_id, db)
            bal = rows.get(leave.leave_type)
            if bal:
                bal.used = max(0, bal.used - leave.days)

    if data.manager_comment:
        leave.manager_comment = data.manager_comment

    await db.flush()
    await db.refresh(leave)
    return LeaveRequestResponse.model_validate(leave)
