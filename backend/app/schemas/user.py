"""User-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ── Auth ────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    department: str = "General"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str


# ── Response ────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    employee_id: str | None = None
    department: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Admin ────────────────────────────────────────────────────────────
class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    employee_id: str | None = None
    department: str
    role: str
    registration_status: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    department: str = "General"
    role: str = Field(default="employee", pattern="^(employee|it_agent|hr_admin|admin)$")
    employee_id: str | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = Field(default=None, pattern="^(employee|it_agent|hr_admin|admin)$")
    registration_status: str | None = Field(default=None, pattern="^(pending|active|suspended)$")
    is_active: bool | None = None
