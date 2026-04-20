"""Analytics response schemas."""

from pydantic import BaseModel


class MessageVolume(BaseModel):
    date: str  # ISO date string "YYYY-MM-DD"
    count: int


class AgentStats(BaseModel):
    agent_name: str
    message_count: int
    positive_feedback: int
    negative_feedback: int
    avg_feedback_score: float | None  # None when no feedback exists


class TicketStatusBreakdown(BaseModel):
    status: str
    count: int


class TicketPriorityBreakdown(BaseModel):
    priority: str
    count: int


class UsersByRole(BaseModel):
    role: str
    count: int


class UsersByDepartment(BaseModel):
    department: str
    count: int


class IntentFrequency(BaseModel):
    intent: str
    count: int


class AnalyticsDashboard(BaseModel):
    # Message volume totals
    messages_last_7d: int
    messages_last_30d: int
    messages_all_time: int

    # Breakdown by agent
    by_agent: list[AgentStats]

    # Daily volume series (last 30 days)
    daily_volume: list[MessageVolume]

    # Ticket stats (None for hr_admin; empty list for admin/it_agent with no data)
    tickets_by_status: list[TicketStatusBreakdown]
    tickets_by_priority: list[TicketPriorityBreakdown]
    avg_resolution_hours: float | None

    # User stats (admin only — None for scoped roles)
    users_by_role: list[UsersByRole] | None
    users_by_department: list[UsersByDepartment] | None

    # Top intents from message metadata
    top_intents: list[IntentFrequency]
