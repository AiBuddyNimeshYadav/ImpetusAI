"""
Ticket Service — CRUD operations for IT tickets.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketDetailResponse, TicketResponse, TicketUpdate
from app.services.it_team import CATEGORY_ASSIGNMENT, MANAGER_MAP, SLA_HOURS, TITLE_MAP


# ── Helpers ──────────────────────────────────────────────────────────

def _ticket_number(ticket_id: str) -> str:
    return f"INC-{ticket_id[:8].upper()}"


def _sla_info(priority: str, created_at: datetime, status: str, resolved_at: datetime | None):
    """Returns (sla_status, sla_deadline, hours_remaining)."""
    sla_h = SLA_HOURS.get(priority, 168)
    created = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
    deadline = created + timedelta(hours=sla_h)
    now = datetime.now(timezone.utc)

    if status in ("resolved", "closed"):
        resolved = resolved_at or now
        if resolved.tzinfo is None:
            resolved = resolved.replace(tzinfo=timezone.utc)
        sla_status = "met" if resolved <= deadline else "breached"
        hours_remaining = None
    else:
        hours_left = (deadline - now).total_seconds() / 3600
        at_risk_threshold = sla_h * 0.2
        if now > deadline:
            sla_status = "breached"
        elif hours_left <= at_risk_threshold:
            sla_status = "at_risk"
        else:
            sla_status = "on_track"
        hours_remaining = round(hours_left, 1)

    return sla_status, deadline, hours_remaining


def enrich(ticket: Ticket, assignee_name: str | None = None) -> TicketResponse:
    """Build a TicketResponse with computed ticket_number, SLA, and assignee name."""
    sla_status, sla_deadline, _ = _sla_info(
        ticket.priority, ticket.created_at, ticket.status, ticket.resolved_at
    )
    resp = TicketResponse.model_validate(ticket)
    resp.ticket_number = _ticket_number(ticket.id)
    resp.sla_status = sla_status
    resp.sla_deadline = sla_deadline
    resp.assigned_to_name = assignee_name
    return resp


# ── Service functions ─────────────────────────────────────────────────

async def create_ticket(db: AsyncSession, user_id: str, data: TicketCreate) -> Ticket:
    """Create a new IT ticket and auto-assign based on category."""
    # Look up the right IT agent for this category
    assignee_email = CATEGORY_ASSIGNMENT.get(data.category, "it.network@impetus.com")
    assignee_result = await db.execute(select(User).where(User.email == assignee_email))
    assignee = assignee_result.scalar_one_or_none()

    ticket = Ticket(
        created_by=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        subcategory=data.subcategory,
        priority=data.priority,
        assigned_to=assignee.id if assignee else None,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def get_tickets(
    db: AsyncSession,
    user_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    role: str = "employee",
) -> list[TicketResponse]:
    """List tickets with optional filters, enriched with SLA and assignee name."""
    query = select(Ticket)
    if role == "employee" and user_id:
        query = query.where(Ticket.created_by == user_id)
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if category:
        query = query.where(Ticket.category == category)
    query = query.order_by(Ticket.created_at.desc())
    result = await db.execute(query)
    tickets = list(result.scalars().all())

    # Batch-load assignee names
    assignee_ids = {t.assigned_to for t in tickets if t.assigned_to}
    assignee_map: dict[str, str] = {}
    if assignee_ids:
        users_result = await db.execute(select(User).where(User.id.in_(assignee_ids)))
        for u in users_result.scalars().all():
            assignee_map[u.id] = u.full_name

    return [enrich(t, assignee_map.get(t.assigned_to)) for t in tickets]


async def get_ticket(db: AsyncSession, ticket_id: str) -> Ticket | None:
    """Get raw ticket ORM object."""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalar_one_or_none()


async def get_ticket_detail(db: AsyncSession, ticket_id: str) -> TicketDetailResponse | None:
    """Return full ticket detail with SLA info, creator, and assignee + manager."""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        return None

    sla_h = SLA_HOURS.get(ticket.priority, 168)
    sla_status, sla_deadline, hours_remaining = _sla_info(
        ticket.priority, ticket.created_at, ticket.status, ticket.resolved_at
    )

    # Creator
    creator_result = await db.execute(select(User).where(User.id == ticket.created_by))
    creator = creator_result.scalar_one_or_none()

    # Assignee
    assignee = None
    assignee_manager = None
    if ticket.assigned_to:
        ar = await db.execute(select(User).where(User.id == ticket.assigned_to))
        assignee = ar.scalar_one_or_none()
        if assignee:
            mgr_email = MANAGER_MAP.get(assignee.email)
            if mgr_email:
                mr = await db.execute(select(User).where(User.email == mgr_email))
                assignee_manager = mr.scalar_one_or_none()

    return TicketDetailResponse(
        id=ticket.id,
        ticket_number=_ticket_number(ticket.id),
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        subcategory=ticket.subcategory,
        priority=ticket.priority,
        status=ticket.status,
        resolution=ticket.resolution,
        conversation_id=ticket.conversation_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        sla_hours=sla_h,
        sla_deadline=sla_deadline,
        sla_status=sla_status,
        sla_hours_remaining=hours_remaining,
        creator_name=creator.full_name if creator else "Unknown",
        creator_email=creator.email if creator else "",
        assignee_id=ticket.assigned_to,
        assignee_name=assignee.full_name if assignee else None,
        assignee_email=assignee.email if assignee else None,
        assignee_title=TITLE_MAP.get(assignee.email) if assignee else None,
        assignee_manager_name=assignee_manager.full_name if assignee_manager else None,
        assignee_manager_email=assignee_manager.email if assignee_manager else None,
    )


async def update_ticket(db: AsyncSession, ticket_id: str, data: TicketUpdate) -> Ticket | None:
    """Update ticket fields."""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        return None

    if data.status:
        ticket.status = data.status
        if data.status in ("resolved", "closed"):
            ticket.resolved_at = datetime.now(timezone.utc)
    if data.priority:
        ticket.priority = data.priority
    if data.assigned_to is not None:
        ticket.assigned_to = data.assigned_to
    if data.resolution:
        ticket.resolution = data.resolution
    if data.category:
        ticket.category = data.category

    return ticket
