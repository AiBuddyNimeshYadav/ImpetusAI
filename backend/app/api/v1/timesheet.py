"""Timesheet API — submit and manage weekly timesheets."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.timesheet import Timesheet
from app.models.user import User
from app.schemas.timesheet import TimesheetCreate, TimesheetResponse, TimesheetUpdate
from ai.agents.timesheet_data import MOCK_PROJECTS

router = APIRouter(prefix="/timesheet", tags=["Timesheet"])


@router.get("/projects")
async def list_projects(current_user: User = Depends(get_current_user)):
    """List available project codes for timesheet entry."""
    return MOCK_PROJECTS


@router.post("", response_model=TimesheetResponse, status_code=201)
async def submit_timesheet(
    data: TimesheetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a weekly timesheet."""
    ts = Timesheet(
        user_id=current_user.id,
        conversation_id=data.conversation_id,
        week_start=data.week_start,
        entries_json=json.dumps([e.model_dump() for e in data.entries]),
        total_hours=data.total_hours,
        status="submitted",
    )
    db.add(ts)
    await db.flush()
    await db.refresh(ts)
    return TimesheetResponse.model_validate(ts)


@router.get("", response_model=list[TimesheetResponse])
async def list_timesheets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List timesheets. Employees see their own; admins/hr_admin see all."""
    query = select(Timesheet).order_by(Timesheet.week_start.desc())
    if current_user.role == "employee":
        query = query.where(Timesheet.user_id == current_user.id)
    result = await db.execute(query)
    return [TimesheetResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/{timesheet_id}", response_model=TimesheetResponse)
async def get_timesheet(
    timesheet_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific timesheet."""
    result = await db.execute(select(Timesheet).where(Timesheet.id == timesheet_id))
    ts = result.scalar_one_or_none()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if current_user.role == "employee" and ts.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return TimesheetResponse.model_validate(ts)


@router.patch("/{timesheet_id}", response_model=TimesheetResponse)
async def update_timesheet(
    timesheet_id: str,
    data: TimesheetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a timesheet (hr_admin / admin only)."""
    if current_user.role not in ("hr_admin", "admin"):
        raise HTTPException(status_code=403, detail="Only HR admins can approve timesheets")
    result = await db.execute(select(Timesheet).where(Timesheet.id == timesheet_id))
    ts = result.scalar_one_or_none()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if data.status:
        ts.status = data.status
        if data.status == "approved":
            ts.approved_by = current_user.id
    if data.manager_comment:
        ts.manager_comment = data.manager_comment
    await db.flush()
    await db.refresh(ts)
    return TimesheetResponse.model_validate(ts)
