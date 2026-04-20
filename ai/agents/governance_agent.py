"""Governance Agent — handles access requests and permission queries."""

import logging
from ai.llm.gateway import get_llm_gateway

logger = logging.getLogger(__name__)

async def handle_governance_request(message: str, history: list[dict] = None) -> str:
    llm = get_llm_gateway()
    
    system_prompt = """You are the ImpetusAI Governance Agent. Your job is to handle requests for elevated access and permissions.

GOALS:
1. Explain the workplace governance process (Requests must be justified and approved by Admins).
2. Help users request roles like 'hr_admin' or 'admin'.
3. Ask for a specific business justification if they haven't provided one.
4. Inform them that while YOU can't grant the role directly, you will guide them to the 'Workplace Governance' portal or help them draft a request.

ROLES AVAILABLE:
- employee (Default)
- hr_admin (Access to Policy Management)
- admin (Full Platform Access)

Tone: Professional, helpful, and firm on security protocols.
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history[-5:])
    messages.append({"role": "user", "content": message})
    
    try:
        response = await llm.generate_with_history(messages)
        return {
            "response_text": response.content,
            "sources": []
        }
    except Exception as e:
        logger.error(f"Governance Agent error: {e}")
        return {
            "response_text": "I'm sorry, I'm having trouble connecting to the governance system. Please try again later or contact your IT administrator.",
            "sources": []
        }
