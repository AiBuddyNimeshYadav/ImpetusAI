"""Governance-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.user import UserResponse

class AccessRequestCreate(BaseModel):
    requested_role: str = Field(..., description="The role being requested (e.g. hr_admin, admin)")
    justification: str = Field(..., min_length=10, description="Business justification for the request")

class AccessRequestProcess(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    admin_comment: str | None = None

class AccessRequestResponse(BaseModel):
    id: str
    user_id: str
    user: UserResponse
    requested_role: str
    justification: str
    status: str
    processed_by: str | None = None
    admin_comment: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class GovernanceStats(BaseModel):
    total_requests: int
    pending_requests: int
    total_users: int
    active_users: int
