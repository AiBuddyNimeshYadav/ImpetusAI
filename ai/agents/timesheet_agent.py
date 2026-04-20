"""Timesheet Submission Agent — natural language timesheet entry and submission."""

import json
import logging
from datetime import date, timedelta

from ai.llm.gateway import get_llm_gateway
from ai.agents.timesheet_data import (
    ACTIVITY_ALIASES,
    ACTIVITY_TYPES,
    MAX_HOURS_PER_DAY,
    MOCK_PROJECTS,
    PROJECT_CODE_MAP,
    STANDARD_HOURS_PER_WEEK,
)

logger = logging.getLogger(__name__)


def _week_start(d: date) -> date:
    """Return Monday of the week containing d."""
    return d - timedelta(days=d.weekday())


def _build_week_dates(week_start: date) -> list[date]:
    """Return Mon–Fri dates for the week."""
    return [week_start + timedelta(days=i) for i in range(5)]


TIMESHEET_SYSTEM = """You are the Timesheet Agent for ImpetusAI at Impetus Technologies.
Help employees log their work hours by extracting project, activity, hours, and dates from natural language.

Today: {today} ({today_day})
Current week: {week_start} to {week_end}
Week dates: {week_dates}

## Available Projects (always show this table when asking about project):
{project_table}

## Available Activity Types (always show this list when asking about activity):
Development · Code Review · Testing/QA · Design · Meeting · Documentation · DevOps/Infra · Client Call · Training · Support · Planning

## CRITICAL RULE — Always show options before asking ANY question:
- If you need to ask for **project** → show the project table above FIRST, then ask which project(s).
- If you need to ask for **activity** → show the activity list above FIRST, then ask which activity.
- If you need to ask for **date/day** → show the current week dates above FIRST (e.g. "Mon 23 Mar, Tue 24 Mar..."), then ask.
- NEVER ask a bare question without showing the relevant options or context.

## Rules:
- Max {max_hours}h per day. Standard week = {std_hours}h.
- Each entry needs: date (or day name), project code, activity, hours.
- You can accept partial entries — if the employee says "8 hours on IMPETUS-AI doing dev today", that's enough.
- When you have at least one complete entry and the employee seems done, output the JSON block below.

## When entries are complete, output ONLY:
```json
{{
  "week_start": "YYYY-MM-DD",
  "entries": [
    {{"date": "YYYY-MM-DD", "day": "Monday", "project_code": "IMPETUS-AI", "project_name": "ImpetusAI Platform", "activity": "Development", "hours": 8, "description": "..."}}
  ],
  "total_hours": <float>,
  "employee_name": "..."
}}
```
TIMESHEET_SUBMIT

Keep responses concise and professional. Never ask more than ONE question per turn."""


async def handle_timesheet(
    message: str,
    history: list[dict] = None,
    employee_name: str = "Employee",
) -> dict:
    """
    Process a timesheet-related message.

    Returns:
        response_text: Markdown response
        action: None | "TIMESHEET_SUBMIT_CONFIRM"
        timesheet_data: dict (if action set)
    """
    llm = get_llm_gateway()
    today = date.today()
    week_start = _week_start(today)
    week_end = week_start + timedelta(days=4)

    # Build week dates string (Mon–Fri with dates)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    week_dates = " · ".join(
        f"{day_names[i]} {(week_start + timedelta(days=i)).strftime('%d %b')}"
        for i in range(5)
    )

    # Build project table for the system prompt
    project_rows = "\n".join(
        f"| {p['code']} | {p['name']} | {'✅ Billable' if p['billable'] else 'Internal'} |"
        for p in MOCK_PROJECTS
    )
    project_table = (
        "| Project Code | Project Name | Type |\n"
        "|--------------|--------------|------|\n"
        + project_rows
    )

    system = TIMESHEET_SYSTEM.format(
        today=today.isoformat(),
        today_day=today.strftime("%A"),
        week_start=week_start.strftime("%d %b %Y"),
        week_end=week_end.strftime("%d %b %Y"),
        week_dates=week_dates,
        project_table=project_table,
        max_hours=MAX_HOURS_PER_DAY,
        std_hours=STANDARD_HOURS_PER_WEEK,
    )

    try:
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(history[-5:])
        messages.append({"role": "user", "content": message})

        llm_response = await llm.generate_with_history(messages)
        response = llm_response.content.strip()

        if "TIMESHEET_SUBMIT" in response:
            response = response.replace("TIMESHEET_SUBMIT", "").strip()
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    raw_json = response[start:end]
                    ts_data = json.loads(raw_json)
                    response_before = response[:start].strip()

                    ts_data["employee_name"] = employee_name
                    entries = ts_data.get("entries", [])
                    total_hours = sum(e.get("hours", 0) for e in entries)
                    ts_data["total_hours"] = total_hours

                    # Validation: check per-day hours
                    day_hours: dict[str, float] = {}
                    for entry in entries:
                        d = entry.get("date", "")
                        day_hours[d] = day_hours.get(d, 0) + entry.get("hours", 0)

                    violations = [
                        f"{d}: {h}h (max {MAX_HOURS_PER_DAY}h)"
                        for d, h in day_hours.items()
                        if h > MAX_HOURS_PER_DAY
                    ]
                    if violations:
                        return {
                            "response_text": f"⚠️ **Hours exceed daily limit ({MAX_HOURS_PER_DAY}h/day)**:\n" + "\n".join(f"- {v}" for v in violations) + "\n\nPlease adjust.",
                            "action": None,
                            "timesheet_data": None,
                        }

                    # Build confirmation table
                    rows = "\n".join(
                        f"| {e.get('day','')[:3]} {e.get('date','')} | {e.get('project_code','')} | {e.get('activity','')} | {e.get('hours','')}h | {e.get('description','')[:40]} |"
                        for e in entries
                    )
                    table = f"""
| Day | Project | Activity | Hours | Description |
|-----|---------|----------|-------|-------------|
{rows}
| **Total** | | | **{total_hours}h** | |
"""
                    response_text = (
                        (response_before + "\n\n" if response_before else "")
                        + f"📋 **Timesheet Summary — Week of {ts_data.get('week_start','')}**\n{table}\n"
                        + "Type **'submit'** or **'confirm'** to submit this timesheet, or tell me what to change."
                    )
                    return {
                        "response_text": response_text.strip(),
                        "action": "TIMESHEET_SUBMIT_CONFIRM",
                        "timesheet_data": ts_data,
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Timesheet agent JSON parse error: {e}")

        # Check for submission confirmation
        message_lower = message.strip().lower()
        if message_lower in ("submit", "confirm", "yes", "go ahead", "looks good"):
            return {
                "response_text": response,
                "action": "TIMESHEET_CONFIRMED",
                "timesheet_data": None,
            }

        return {"response_text": response, "action": None, "timesheet_data": None}

    except Exception as e:
        logger.error(f"Timesheet agent error: {type(e).__name__}: {e}")
        return {
            "response_text": "I encountered an error while processing your timesheet. Please try again.",
            "action": None,
            "timesheet_data": None,
        }
