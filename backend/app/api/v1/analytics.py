"""Analytics API — role-scoped dashboard data."""

import json
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.conversation import Message
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.analytics import (
    AgentStats,
    AnalyticsDashboard,
    IntentFrequency,
    MessageVolume,
    TicketPriorityBreakdown,
    TicketStatusBreakdown,
    UsersByDepartment,
    UsersByRole,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Role → allowed agent_name values (None = no filter = admin sees everything)
_AGENT_SCOPE: dict[str, list[str] | None] = {
    "admin": None,
    "hr_admin": ["hr_policy", "general"],
    "it_agent": ["it_support", "general"],
}


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsDashboard:
    """Return role-scoped analytics dashboard data."""
    if current_user.role not in _AGENT_SCOPE:
        raise HTTPException(status_code=403, detail="Access denied")

    agent_scope = _AGENT_SCOPE[current_user.role]
    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    # ── Message volume totals ────────────────────────────────────────
    def _base_count_q():
        return select(func.count(Message.id)).where(Message.role == "assistant")

    def _scope(q):
        if agent_scope is not None:
            return q.where(Message.agent_name.in_(agent_scope))
        return q

    messages_all_time = (await db.execute(_scope(_base_count_q()))).scalar() or 0
    messages_last_7d = (
        await db.execute(_scope(_base_count_q().where(Message.created_at >= cutoff_7d)))
    ).scalar() or 0
    messages_last_30d = (
        await db.execute(_scope(_base_count_q().where(Message.created_at >= cutoff_30d)))
    ).scalar() or 0

    # ── By-agent stats ───────────────────────────────────────────────
    agent_q = (
        select(
            Message.agent_name,
            func.count(Message.id).label("message_count"),
            func.sum(case((Message.feedback == 1, 1), else_=0)).label("positive"),
            func.sum(case((Message.feedback == -1, 1), else_=0)).label("negative"),
            func.avg(Message.feedback).label("avg_feedback"),
        )
        .where(Message.role == "assistant")
        .where(Message.agent_name.isnot(None))
        .group_by(Message.agent_name)
    )
    agent_q = _scope(agent_q)
    agent_rows = (await db.execute(agent_q)).all()

    by_agent = [
        AgentStats(
            agent_name=row.agent_name,
            message_count=row.message_count,
            positive_feedback=row.positive or 0,
            negative_feedback=row.negative or 0,
            avg_feedback_score=(
                round(float(row.avg_feedback), 2) if row.avg_feedback is not None else None
            ),
        )
        for row in agent_rows
    ]

    # ── Daily volume (last 30 days) ──────────────────────────────────
    daily_q = (
        select(
            func.strftime("%Y-%m-%d", Message.created_at).label("day"),
            func.count(Message.id).label("count"),
        )
        .where(Message.role == "assistant")
        .where(Message.created_at >= cutoff_30d)
        .group_by(text("day"))
        .order_by(text("day"))
    )
    daily_q = _scope(daily_q)
    daily_rows = (await db.execute(daily_q)).all()
    daily_volume = [MessageVolume(date=row.day, count=row.count) for row in daily_rows]

    # ── Ticket stats (admin + it_agent only) ─────────────────────────
    tickets_by_status: list[TicketStatusBreakdown] = []
    tickets_by_priority: list[TicketPriorityBreakdown] = []
    avg_resolution_hours: float | None = None

    if current_user.role in ("admin", "it_agent"):
        status_rows = (
            await db.execute(
                select(Ticket.status, func.count(Ticket.id).label("count")).group_by(Ticket.status)
            )
        ).all()
        tickets_by_status = [
            TicketStatusBreakdown(status=r.status, count=r.count) for r in status_rows
        ]

        priority_rows = (
            await db.execute(
                select(Ticket.priority, func.count(Ticket.id).label("count")).group_by(
                    Ticket.priority
                )
            )
        ).all()
        tickets_by_priority = [
            TicketPriorityBreakdown(priority=r.priority, count=r.count) for r in priority_rows
        ]

        avg_row = (
            await db.execute(
                select(
                    func.avg(
                        (
                            func.julianday(Ticket.resolved_at)
                            - func.julianday(Ticket.created_at)
                        )
                        * 24
                    ).label("avg_hours")
                ).where(Ticket.resolved_at.isnot(None))
            )
        ).scalar()
        avg_resolution_hours = round(float(avg_row), 1) if avg_row is not None else None

    # ── User breakdowns (admin only) ─────────────────────────────────
    users_by_role: list[UsersByRole] | None = None
    users_by_department: list[UsersByDepartment] | None = None

    if current_user.role == "admin":
        role_rows = (
            await db.execute(
                select(User.role, func.count(User.id).label("count")).group_by(User.role)
            )
        ).all()
        users_by_role = [UsersByRole(role=r.role, count=r.count) for r in role_rows]

        dept_rows = (
            await db.execute(
                select(User.department, func.count(User.id).label("count")).group_by(
                    User.department
                )
            )
        ).all()
        users_by_department = [
            UsersByDepartment(department=r.department, count=r.count) for r in dept_rows
        ]

    # ── Top 5 intents (parsed from metadata_json in Python) ──────────
    meta_q = _scope(
        select(Message.metadata_json)
        .where(Message.role == "assistant")
        .where(Message.metadata_json.isnot(None))
    )
    meta_rows = (await db.execute(meta_q)).scalars().all()

    intent_counter: Counter = Counter()
    for raw in meta_rows:
        try:
            parsed = json.loads(raw)
            intent = parsed.get("intent")
            if intent:
                intent_counter[intent] += 1
        except (json.JSONDecodeError, AttributeError):
            continue

    top_intents = [
        IntentFrequency(intent=intent, count=count)
        for intent, count in intent_counter.most_common(5)
    ]

    return AnalyticsDashboard(
        messages_last_7d=messages_last_7d,
        messages_last_30d=messages_last_30d,
        messages_all_time=messages_all_time,
        by_agent=by_agent,
        daily_volume=daily_volume,
        tickets_by_status=tickets_by_status,
        tickets_by_priority=tickets_by_priority,
        avg_resolution_hours=avg_resolution_hours,
        users_by_role=users_by_role,
        users_by_department=users_by_department,
        top_intents=top_intents,
    )
