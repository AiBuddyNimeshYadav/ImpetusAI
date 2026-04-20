"""Tickets API — CRUD for IT support tickets."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketDetailResponse
from app.services import ticket_service
from app.services.it_team import TITLE_MAP

router = APIRouter(prefix="/tickets", tags=["Tickets"])


class AssigneeOption(BaseModel):
    id: str
    full_name: str
    email: str
    title: str


@router.get("/assignees", response_model=list[AssigneeOption])
async def list_assignees(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all IT agents available for ticket assignment."""
    result = await db.execute(select(User).where(User.role == "it_agent", User.is_active == True))
    agents = result.scalars().all()
    return [
        AssigneeOption(
            id=a.id,
            full_name=a.full_name,
            email=a.email,
            title=TITLE_MAP.get(a.email, "IT Agent"),
        )
        for a in agents
    ]


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new IT ticket (auto-assigned based on category)."""
    ticket = await ticket_service.create_ticket(db, current_user.id, data)
    return ticket_service.enrich(ticket)


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tickets. Employees see their own; admins/IT agents see all."""
    return await ticket_service.get_tickets(
        db,
        user_id=current_user.id,
        status=status,
        priority=priority,
        category=category,
        role=current_user.role,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full ticket detail with SLA, assignee, and manager info."""
    raw = await ticket_service.get_ticket(db, ticket_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == "employee" and raw.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await ticket_service.get_ticket_detail(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketDetailResponse)
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a ticket (status, priority, assignment, resolution)."""
    if current_user.role not in ("it_agent", "admin", "hr_admin"):
        raise HTTPException(status_code=403, detail="Only IT agents and admins can update tickets")
    ticket = await ticket_service.update_ticket(db, ticket_id, data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return await ticket_service.get_ticket_detail(db, ticket_id)
