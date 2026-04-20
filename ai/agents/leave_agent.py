"""Leave Application Agent — handles leave requests, balance queries, cancellations."""

import json
import logging
import re
from datetime import date, datetime, timedelta

from ai.llm.gateway import get_llm_gateway
from ai.agents.leave_data import (
    DEFAULT_BALANCES,
    LEAVE_TYPES,
    PUBLIC_HOLIDAYS,
    HOLIDAY_NAMES,
)

logger = logging.getLogger(__name__)

LEAVE_AGENT_SYSTEM = """You are the Leave Management Agent for ImpetusAI at Impetus Technologies.
You help employees apply for leave, check balances, and manage requests through natural conversation.

Current leave balances for this employee:
{balance_table}

Today's date: {today}

---

## How to handle leave applications

**Step 1 — Gather details**
From the employee's message, extract whatever is already given:
- Leave type: recognise CL / casual / casual leave, EL / earned / privilege, SL / sick, CO / comp-off / comp off
- Start date: recognise "01-April", "1 Apr", "April 1st", "01/04/2026", "next Monday", "tomorrow" etc. (assume year 2026 if not stated)
- End date or duration: "to 02-Apr", "2 days", "till Friday" etc.
- Reason: optional — accept if given naturally ("for a wedding", "feeling unwell", "planned leave"), never demand it

If ALL three (type + start + end/duration) are present in the message, proceed directly to Step 2.
If something is missing, ask ONLY for that one missing piece. Show the balance table when asking about leave type.

**Step 2 — When you have all details, output this exact block (no other text around it):**
<<LEAVE_REQUEST>>
{{"leave_type": "CL", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "reason": "reason or Not specified"}}
<</LEAVE_REQUEST>>

**Step 3 — After the summary is shown, watch for confirmation**
The employee may confirm in many natural ways:
- "yes", "confirm", "ok", "go ahead", "submit it", "please proceed"
- "yes, reason is planned leave" → reason = "planned leave"
- "confirmed, it's for a family trip" → reason = "family trip"
- "yes please proceed" → no reason update, use null

When you detect confirmation, output ONLY this block (no other text):
<<LEAVE_SUBMIT>>
{{"confirmed": true, "reason": "<ONLY the reason phrase the user stated, e.g. planned leave — or null if not stated>"}}
<</LEAVE_SUBMIT>>

IMPORTANT: Extract ONLY the bare reason phrase. Do NOT include words like "reason is", "reason =", "confirm", or the full sentence. If no reason was given, set reason to null.

If the employee wants to change something (dates, type), restart from Step 1 with the new info.
If they want to cancel, output:
<<LEAVE_SUBMIT>>
{{"confirmed": false, "reason": null}}
<</LEAVE_SUBMIT>>

---

## Other requests
- Balance check → show the balance table nicely
- Status / history → explain they can check the Leave tab
- Cancellation of existing leave → ask for the reference number (format LV-XXXXXXXX)
- Keep all responses concise and friendly"""


def _count_working_days(start: date, end: date) -> int:
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in PUBLIC_HOLIDAYS:
            count += 1
        current += timedelta(days=1)
    return count


def _adjacent_holidays(start: date, end: date) -> list[str]:
    adjacent = []
    if (start - timedelta(days=1)) in PUBLIC_HOLIDAYS:
        d = start - timedelta(days=1)
        adjacent.append(f"{HOLIDAY_NAMES[d]} on {d.strftime('%d %b')}")
    if (end + timedelta(days=1)) in PUBLIC_HOLIDAYS:
        d = end + timedelta(days=1)
        adjacent.append(f"{HOLIDAY_NAMES[d]} on {d.strftime('%d %b')}")
    return adjacent


def _build_summary(leave_data: dict, balances: dict) -> str:
    leave_type = leave_data.get("leave_type", "CL")
    start_date = datetime.strptime(leave_data["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(leave_data["end_date"], "%Y-%m-%d").date()
    working_days = _count_working_days(start_date, end_date)
    leave_data["days"] = working_days

    available = balances.get(leave_type, 0)
    lt_name = LEAVE_TYPES.get(leave_type, {}).get("name", leave_type)
    reason = leave_data.get("reason") or "Not specified"

    adj = _adjacent_holidays(start_date, end_date)
    tip = ""
    if adj:
        tip = f"\n\n> 💡 **Tip:** There's a public holiday adjacent to your leave — {', '.join(adj)}. You could extend for a longer break!"

    return (
        f"Here's a summary of your leave request:\n\n"
        f"| Field | Details |\n"
        f"|-------|---------|\n"
        f"| **Leave Type** | {lt_name} ({leave_type}) |\n"
        f"| **From** | {start_date.strftime('%d %b %Y (%A)')} |\n"
        f"| **To** | {end_date.strftime('%d %b %Y (%A)')} |\n"
        f"| **Working Days** | {working_days} day{'s' if working_days != 1 else ''} |\n"
        f"| **Balance Available** | {available} day(s) |\n"
        f"| **Balance After Approval** | {available - working_days} day(s) |\n"
        f"| **Reason** | {reason} |\n"
        f"{tip}\n\n"
        f"Please confirm to submit, or let me know if you'd like to change anything."
    )


async def handle_leave_request(
    message: str,
    history: list[dict] = None,
    user_balances: dict = None,
    employee_name: str = "Employee",
) -> dict:
    llm = get_llm_gateway()
    balances = user_balances or DEFAULT_BALANCES
    today = date.today().isoformat()

    ANNUAL_TOTAL = {"CL": 12, "EL": 18, "SL": 10, "CO": 4}
    balance_table_rows = "\n".join(
        f"| {LEAVE_TYPES[k]['name']} | **{k}** | {v} days | {max(0, ANNUAL_TOTAL.get(k, DEFAULT_BALANCES.get(k, 0)) - v)} used |"
        for k, v in balances.items()
        if k in LEAVE_TYPES
    )
    balance_table = (
        "| Leave Type | Code | Available | Used |\n"
        "|------------|------|-----------|------|\n"
        + balance_table_rows
    )
    system = LEAVE_AGENT_SYSTEM.format(today=today, balance_table=balance_table)

    try:
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(history[-8:])
        messages.append({"role": "user", "content": message})

        llm_response = await llm.generate_with_history(messages)
        response = llm_response.content.strip()

        # ── Detect <<LEAVE_SUBMIT>> — user confirmed ───────────────────
        submit_match = re.search(r"<<LEAVE_SUBMIT>>(.*?)<</LEAVE_SUBMIT>>", response, re.DOTALL)
        if submit_match:
            try:
                submit_data = json.loads(submit_match.group(1).strip())
                if submit_data.get("confirmed") is False:
                    return {"response_text": "No problem — your leave request has been cancelled. Let me know if you'd like to apply for different dates.", "action": None, "leave_data": None}
                # Pass reason update back so chat_service can patch pending_leave
                return {
                    "response_text": "",
                    "action": "LEAVE_CONFIRMED",
                    "leave_data": {"reason_update": submit_data.get("reason")},
                }
            except json.JSONDecodeError:
                pass

        # ── Detect <<LEAVE_REQUEST>> — new leave details ready ─────────
        request_match = re.search(r"<<LEAVE_REQUEST>>(.*?)<</LEAVE_REQUEST>>", response, re.DOTALL)
        if request_match:
            try:
                leave_data = json.loads(request_match.group(1).strip())
                leave_data["employee_name"] = employee_name

                leave_type = leave_data.get("leave_type", "CL")
                start_date = datetime.strptime(leave_data["start_date"], "%Y-%m-%d").date()
                end_date = datetime.strptime(leave_data["end_date"], "%Y-%m-%d").date()
                working_days = _count_working_days(start_date, end_date)
                leave_data["days"] = working_days

                available = balances.get(leave_type, 0)
                if working_days > available:
                    return {
                        "response_text": (
                            f"⚠️ **Insufficient Leave Balance** — you only have **{available} {leave_type} day(s)** "
                            f"remaining but this request needs **{working_days} day(s)**. "
                            f"Please choose different dates or a different leave type."
                        ),
                        "action": None,
                        "leave_data": None,
                    }

                return {
                    "response_text": _build_summary(leave_data, balances),
                    "action": "LEAVE_REQUEST_CONFIRM",
                    "leave_data": leave_data,
                }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"Leave agent <<LEAVE_REQUEST>> parse error: {e}")

        # ── Fallback: scan for stray JSON with leave_type + start_date ──
        for match in re.finditer(r"\{[^{}]+\}", response, re.DOTALL):
            try:
                candidate = json.loads(match.group())
                if "leave_type" in candidate and "start_date" in candidate:
                    candidate["employee_name"] = employee_name
                    leave_type = candidate.get("leave_type", "CL")
                    start_date = datetime.strptime(candidate["start_date"], "%Y-%m-%d").date()
                    end_date = datetime.strptime(candidate["end_date"], "%Y-%m-%d").date()
                    working_days = _count_working_days(start_date, end_date)
                    candidate["days"] = working_days
                    available = balances.get(leave_type, 0)
                    if working_days <= available:
                        clean = (response[:match.start()] + response[match.end():]).strip()
                        clean = re.sub(r"```(?:json)?\s*```", "", clean).strip()
                        return {
                            "response_text": _build_summary(candidate, balances),
                            "action": "LEAVE_REQUEST_CONFIRM",
                            "leave_data": candidate,
                        }
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return {"response_text": response, "action": None, "leave_data": None}

    except Exception as e:
        logger.error(f"Leave agent error: {type(e).__name__}: {e}")
        return {
            "response_text": "I encountered an error processing your request. Please try again.",
            "action": None,
            "leave_data": None,
        }
