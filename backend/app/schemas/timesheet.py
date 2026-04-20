"""Timesheet Pydantic schemas."""

import json
from datetime import date, datetime
from pydantic import BaseModel, model_validator


class TimesheetEntry(BaseModel):
    date: str
    day: str
    project_code: str
    project_name: str
    activity: str
    hours: float
    description: str = ""


class TimesheetCreate(BaseModel):
    week_start: date
    entries: list[TimesheetEntry]
    total_hours: float
    conversation_id: str | None = None


class TimesheetUpdate(BaseModel):
    status: str | None = None       # approved, rejected
    manager_comment: str | None = None


class TimesheetResponse(BaseModel):
    id: str
    user_id: str
    week_start: date
    entries: list[TimesheetEntry] = []
    total_hours: float
    status: str
    manager_comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def parse_entries_json(cls, values):
        """Convert entries_json string to list if needed."""
        if hasattr(values, "__dict__"):
            # ORM object
            raw = getattr(values, "entries_json", "[]")
            if isinstance(raw, str):
                values.__dict__["entries"] = json.loads(raw)
        elif isinstance(values, dict) and "entries_json" in values:
            raw = values.pop("entries_json", "[]")
            if isinstance(raw, str):
                values["entries"] = json.loads(raw)
        return values
