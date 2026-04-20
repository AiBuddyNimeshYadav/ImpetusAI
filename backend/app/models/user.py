"""User model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    department: Mapped[str] = mapped_column(String(100), default="General")
    role: Mapped[str] = mapped_column(String(50), default="employee")  # employee, it_agent, hr_admin, admin
    registration_status: Mapped[str] = mapped_column(String(20), default="active") # pending, active, suspended
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    conversations = relationship("Conversation", back_populates="user", lazy="selectin")
    access_requests = relationship("AccessRequest", back_populates="user", foreign_keys="[AccessRequest.user_id]", lazy="selectin")
