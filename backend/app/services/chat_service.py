"""
Chat Service — Manages conversations and orchestrates AI agents.

Routes user messages through the Supervisor → specialized agent pipeline.
"""

import json
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.models.ticket import Ticket
from app.models.leave_request import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.models.timesheet import Timesheet
from app.models.user import User as UserModel
from app.services.it_team import CATEGORY_ASSIGNMENT
from ai.agents.supervisor import classify_intent
from ai.agents.it_support import handle_it_issue
from ai.agents.hr_policy import answer_hr_query
from ai.agents.governance_agent import handle_governance_request
from ai.agents.leave_agent import handle_leave_request
from ai.agents.timesheet_agent import handle_timesheet
from ai.llm.gateway import get_llm_gateway

logger = logging.getLogger(__name__)

GENERAL_SYSTEM = """You are ImpetusAI, a helpful AI assistant for employees at Impetus Technologies.
You can help with:
- IT Support: Report issues, get troubleshooting help, create tickets
- HR Policies: Ask about leave, benefits, code of conduct, remote work
- General Questions: Anything work-related

Be friendly, professional, and concise. Use markdown for formatting.
If the user seems to have an IT issue or HR question, guide them accordingly.
"""


async def send_message(
    db: AsyncSession,
    user_id: str,
    message: str,
    conversation_id: str | None = None,
) -> dict:
    """
    Process a user message through the AI pipeline.

    Steps:
    1. Get or create conversation
    2. Classify intent via Supervisor
    3. Route to specialized agent
    4. Store messages and return response
    """
    # 1. Get or create conversation
    conversation = None
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.flush()

    # 2. Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )
    db.add(user_msg)
    await db.flush()

    # 3. Build conversation history for context
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    all_messages = result.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in all_messages[-10:]]

    # 4. Classify intent
    classification = await classify_intent(message, history)
    intent = classification["intent"]
    logger.info(f"Intent: {intent} (confidence: {classification['confidence']})")

    # 5. Route to specialized agent
    response_text = ""
    agent_name = "supervisor"
    ticket_created = False
    ticket_id = None
    ai_msg_meta: dict = {"intent": intent, "confidence": classification["confidence"], "ticket_created": False}

    if intent == "it_support":
        agent_name = "it_support"
        result = await handle_it_issue(message, history)
        response_text = result["response_text"]

        # Auto-create ticket if the agent recommends it
        if result.get("should_create_ticket") and result.get("ticket"):
            t = result["ticket"]
            category = t.get("category", "General")
            # Auto-assign to the right IT agent
            assignee_email = CATEGORY_ASSIGNMENT.get(category, "it.network@impetus.com")
            assignee_res = await db.execute(
                select(UserModel).where(UserModel.email == assignee_email)
            )
            assignee = assignee_res.scalar_one_or_none()
            ticket = Ticket(
                conversation_id=conversation.id,
                created_by=user_id,
                title=t.get("title", message[:100]),
                description=t.get("description", message),
                category=category,
                priority=t.get("priority", "P3"),
                assigned_to=assignee.id if assignee else None,
            )
            db.add(ticket)
            await db.flush()
            ticket_created = True
            ticket_id = ticket.id
            inc_num = f"INC-{ticket.id[:8].upper()}"
            assignee_name = assignee.full_name if assignee else "Unassigned"
            response_text += f"\n\n📋 **Ticket Created** — **{inc_num}** | Priority: {ticket.priority} | Category: {ticket.category} | Assigned to: {assignee_name}"
            ai_msg_meta["ticket_created"] = True

    elif intent == "hr_policy":
        agent_name = "HR Policy Agent"
        result = await answer_hr_query(message, history)
        response_text = result["response_text"]
        if result.get("sources"):
            links = [f"[{s.replace('_', ' ').replace('.md', '').replace('.pdf', '').title()}](/api/v1/documents/policy/{s})" for s in result["sources"]]
            response_text += "\n\n📄 **Sources:** " + " · ".join(links)

    elif intent == "governance":
        agent_name = "Governance Agent"
        result = await handle_governance_request(message, history)
        response_text = result["response_text"]
        if result.get("sources"):
            links = [f"[{s.replace('_', ' ').replace('.md', '').replace('.pdf', '').title()}](/api/v1/documents/policy/{s})" for s in result["sources"]]
            response_text += "\n\n📄 **Sources:** " + " · ".join(links)

    elif intent == "leave_request":
        agent_name = "Leave Agent"
        # Fetch current user info and pending leave context
        user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        current_user = user_result.scalar_one_or_none()
        employee_name = current_user.full_name if current_user else "Employee"

        # Load live balances from LeaveBalance table (per-user, per-year)
        import datetime as _dt
        current_year = _dt.date.today().year
        from ai.agents.leave_data import DEFAULT_ANNUAL_ALLOCATION
        bal_result = await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == user_id,
                LeaveBalance.year == current_year,
            )
        )
        bal_rows = {b.leave_type: b for b in bal_result.scalars().all()}

        # If no rows exist yet (new user), seed them now
        if not bal_rows:
            for lt, total in DEFAULT_ANNUAL_ALLOCATION.items():
                new_bal = LeaveBalance(user_id=user_id, leave_type=lt, year=current_year, total_allocated=total, used=0)
                db.add(new_bal)
            await db.flush()
            bal_result2 = await db.execute(
                select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == current_year)
            )
            bal_rows = {b.leave_type: b for b in bal_result2.scalars().all()}

        live_balances = {lt: max(0, b.total_allocated - b.used) for lt, b in bal_rows.items()}

        result = await handle_leave_request(message, history, live_balances, employee_name)
        response_text = result["response_text"]

        # Store pending leave data in conversation metadata for next-turn confirmation
        if result.get("action") == "LEAVE_REQUEST_CONFIRM" and result.get("leave_data"):
            ai_msg_meta = {
                "intent": intent,
                "confidence": classification["confidence"],
                "ticket_created": False,
                "pending_leave": result["leave_data"],
            }
        elif result.get("action") == "LEAVE_CONFIRMED":
            # Find pending leave stored in recent assistant messages
            recent = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation.id, Message.role == "assistant")
                .order_by(Message.created_at.desc())
                .limit(5)
            )
            pending_leave = None
            for msg in recent.scalars().all():
                try:
                    meta = json.loads(msg.metadata_json or "{}")
                    if meta.get("pending_leave"):
                        pending_leave = meta["pending_leave"]
                        break
                except (json.JSONDecodeError, AttributeError):
                    pass

            if pending_leave:
                from datetime import date as _date
                # Allow reason update from LLM's LEAVE_SUBMIT payload
                reason_update = (result.get("leave_data") or {}).get("reason_update")
                if reason_update and isinstance(reason_update, str):
                    # Strip common LLM noise like "reason is", "reason =", "Reason:"
                    import re as _re
                    clean_reason = _re.sub(
                        r"(?i)^(reason\s*(is|=|:)\s*|i confirm\s*(with\s*)?(reason\s*(is|=|:)\s*)?)",
                        "", reason_update
                    ).strip().strip('"').strip("'")
                    if clean_reason:
                        pending_leave = {**pending_leave, "reason": clean_reason}

                leave_type = pending_leave["leave_type"]
                days = pending_leave["days"]

                balance_row = bal_rows.get(leave_type)
                available = max(0, balance_row.total_allocated - balance_row.used) if balance_row else 0
                if available < days:
                    response_text = (
                        f"⚠️ **Insufficient Balance** — you only have {available} {leave_type} day(s) remaining "
                        f"but this request needs {days} day(s). Please choose different dates or a different leave type."
                    )
                else:
                    leave = LeaveRequest(
                        user_id=user_id,
                        conversation_id=conversation.id,
                        leave_type=leave_type,
                        start_date=_date.fromisoformat(pending_leave["start_date"]),
                        end_date=_date.fromisoformat(pending_leave["end_date"]),
                        days=days,
                        reason=pending_leave.get("reason"),
                        status="pending",
                    )
                    db.add(leave)
                    await db.flush()
                    leave.reference = f"LV-{leave.id[:8].upper()}"

                    if balance_row:
                        balance_row.used = balance_row.used + days
                    await db.flush()

                    lt_name = {"CL": "Casual Leave", "EL": "Earned Leave", "SL": "Sick Leave", "CO": "Comp-Off"}.get(leave_type, leave_type)
                    s_date = _date.fromisoformat(pending_leave["start_date"])
                    e_date = _date.fromisoformat(pending_leave["end_date"])
                    new_available = max(0, balance_row.total_allocated - balance_row.used) if balance_row else 0
                    reason_val = pending_leave.get("reason") or "Not specified"
                    response_text = (
                        f"Your **{lt_name}** has been applied successfully.\n\n"
                        f"**{s_date.strftime('%d %b %Y')}** to **{e_date.strftime('%d %b %Y')}** "
                        f"({days} working day{'s' if days != 1 else ''}) · Reason: {reason_val}\n\n"
                        f"**Reference:** {leave.reference}  \n"
                        f"**Status:** Pending approval — your manager will review shortly.\n\n"
                        f"**Remaining {leave_type} balance:** {new_available} day(s)"
                    )
            else:
                response_text = (
                    "I couldn't find a pending leave request to confirm. "
                    "Please describe your leave again (type and dates) and I'll prepare a fresh summary."
                )

    elif intent == "timesheet":
        agent_name = "Timesheet Agent"
        user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        current_user = user_result.scalar_one_or_none()
        employee_name = current_user.full_name if current_user else "Employee"

        result = await handle_timesheet(message, history, employee_name)
        response_text = result["response_text"]

        if result.get("action") == "TIMESHEET_SUBMIT_CONFIRM" and result.get("timesheet_data"):
            ai_msg_meta = {
                "intent": intent,
                "confidence": classification["confidence"],
                "ticket_created": False,
                "pending_timesheet": result["timesheet_data"],
            }
        elif result.get("action") == "TIMESHEET_CONFIRMED":
            recent = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation.id, Message.role == "assistant")
                .order_by(Message.created_at.desc())
                .limit(3)
            )
            pending_ts = None
            for msg in recent.scalars().all():
                try:
                    meta = json.loads(msg.metadata_json or "{}")
                    if meta.get("pending_timesheet"):
                        pending_ts = meta["pending_timesheet"]
                        break
                except (json.JSONDecodeError, AttributeError):
                    pass

            if pending_ts:
                from datetime import date as _date
                ts = Timesheet(
                    user_id=user_id,
                    conversation_id=conversation.id,
                    week_start=_date.fromisoformat(pending_ts["week_start"]),
                    entries_json=json.dumps(pending_ts.get("entries", [])),
                    total_hours=pending_ts.get("total_hours", 0),
                    status="submitted",
                )
                db.add(ts)
                await db.flush()
                response_text = f"✅ **Timesheet Submitted!**\n\nYour timesheet for the week of **{pending_ts['week_start']}** ({pending_ts.get('total_hours', 0)}h total) has been submitted for approval."

    else:
        agent_name = "General Assistant"
        llm = get_llm_gateway()
        resp = await llm.generate_with_history(
            messages=history,
            system_message=GENERAL_SYSTEM,
            temperature=0.5,
        )
        response_text = resp.content

    # 6. Update conversation metadata
    if conversation.title == "New Conversation" or not conversation.title:
        conversation.title = classification["summary"][:100]
    conversation.module = intent

    # 7. Store assistant message
    ai_msg_meta["ticket_created"] = ticket_created
    ai_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        agent_name=agent_name,
        metadata_json=json.dumps(ai_msg_meta),
    )
    db.add(ai_msg)
    await db.flush()
    await db.refresh(ai_msg)

    return {
        "conversation_id": conversation.id,
        "message": ai_msg,
        "agent_name": agent_name,
        "ticket_created": ticket_created,
        "ticket_id": ticket_id,
    }


async def get_conversations(db: AsyncSession, user_id: str) -> list[Conversation]:
    """Get all conversations for a user, newest first."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation(
    db: AsyncSession, user_id: str, conversation_id: str
) -> Conversation | None:
    """Get a single conversation with messages."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def submit_feedback(
    db: AsyncSession, message_id: str, feedback: int, comment: str | None = None
) -> bool:
    """Submit feedback on an AI message."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        return False
    msg.feedback = feedback
    msg.feedback_comment = comment
    return True


async def rename_conversation(
    db: AsyncSession, user_id: str, conversation_id: str, new_title: str
) -> Conversation | None:
    """Rename a conversation."""
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        return None

    conv.title = new_title
    await db.flush()
    await db.refresh(conv)
    return conv


async def delete_conversation(
    db: AsyncSession, user_id: str, conversation_id: str
) -> bool:
    """Delete a conversation and all its messages."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        return False

    # Delete messages first
    await db.execute(delete(Message).where(Message.conversation_id == conversation_id))
    
    # Unlink any tickets before deleting (so tickets aren't deleted but conversation reference is nulled)
    await db.execute(
        Ticket.__table__.update().where(Ticket.conversation_id == conversation_id).values(conversation_id=None)
    )

    # Delete the conversation
    await db.delete(conv)
    await db.flush()
    return True
