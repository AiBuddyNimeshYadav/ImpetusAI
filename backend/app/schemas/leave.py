"""Leave request Pydantic schemas."""

from datetime import date, datetime
from pydantic import BaseModel


class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: str | None = None
    conversation_id: str | None = None


class LeaveRequestUpdate(BaseModel):
    status: str | None = None       # approved, rejected, cancelled
    manager_comment: str | None = None


class LeaveRequestResponse(BaseModel):
    id: str
    reference: str | None
    user_id: str
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: str | None
    status: str
    manager_comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaveBalanceResponse(BaseModel):
    CL: int
    EL: int
    SL: int
    CO: int
