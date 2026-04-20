"""Ticket-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    category: str = "General"
    subcategory: str | None = None
    priority: str = "P3"


class TicketUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to: str | None = None
    resolution: str | None = None
    category: str | None = None


class TicketResponse(BaseModel):
    id: str
    ticket_number: str = ""       # computed: INC-XXXXXXXX
    title: str
    description: str
    category: str
    subcategory: str | None = None
    priority: str
    status: str
    resolution: str | None = None
    created_by: str
    assigned_to: str | None = None
    assigned_to_name: str | None = None   # enriched
    conversation_id: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    sla_status: str = ""          # on_track | at_risk | breached | met
    sla_deadline: datetime | None = None

    model_config = {"from_attributes": True}


class TicketDetailResponse(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    category: str
    subcategory: str | None = None
    priority: str
    status: str
    resolution: str | None = None
    conversation_id: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    # SLA
    sla_hours: int
    sla_deadline: datetime
    sla_status: str
    sla_hours_remaining: float | None
    # People
    creator_name: str
    creator_email: str
    assignee_id: str | None
    assignee_name: str | None
    assignee_email: str | None
    assignee_title: str | None
    assignee_manager_name: str | None
    assignee_manager_email: str | None

    model_config = {"from_attributes": False}
