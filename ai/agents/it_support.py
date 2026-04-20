import logging
import json
from ai.llm.gateway import get_llm_gateway

logger = logging.getLogger(__name__)

async def handle_it_issue(message: str, history: list[dict] = None) -> dict:
    llm = get_llm_gateway()
    prompt = """You are an IT Support Agent. Help the user troubleshoot.
If the issue cannot be resolved immediately and warrants a ticket, output a JSON block ending with 'TICKET_REQUIRED' as the last line.
JSON format: {"title": "Short title", "priority": "P1/P2/P3/P4", "category": "Network/Hardware/Access/Software"}
"""
    try:
        messages = [{"role": "system", "content": prompt}]
        if history:
            messages.extend(history[-3:])
        messages.append({"role": "user", "content": message})
        
        llm_response = await llm.generate_with_history(messages)
        response = llm_response.content
        
        create_ticket = False
        ticket_data = None
        
        if "TICKET_REQUIRED" in response:
            create_ticket = True
            response = response.replace("TICKET_REQUIRED", "").strip()
            # Try parsing JSON from response
            try:
                # Find JSON block
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    target_json = response[start:end]
                    ticket_data = json.loads(target_json)
                    response = response[:start].strip() + "\n\n" + response[end:].strip()
            except Exception as e:
                logger.error(f"JSON parsing error: {e}")
                
        return {
            "response_text": response.strip(),
            "should_create_ticket": create_ticket,
            "ticket": ticket_data
        }
    except Exception as e:
        logger.error(f"IT Support error: {e}")
        return {"response_text": "I encountered an error while processing your IT request.", "should_create_ticket": False, "ticket": None}
