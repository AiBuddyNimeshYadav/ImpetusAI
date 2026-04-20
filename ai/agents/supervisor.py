import logging
import json
from ai.llm.gateway import get_llm_gateway

logger = logging.getLogger(__name__)

VALID_INTENTS = ['it_support', 'hr_policy', 'governance', 'leave_request', 'timesheet', 'general']

async def classify_intent(message: str, history: list[dict] = None) -> dict:
    llm = get_llm_gateway()
    prompt = """Analyze the user's message and determine the intent.
Classify the intent strictly into one of these categories:
1. 'it_support' (IT issues, VPN, hardware, software, access problems, device issues)
2. 'hr_policy' (HR policy questions, benefits, code of conduct, remote work policy)
3. 'governance' (Access requests, admin rights, permission issues, role changes)
4. 'leave_request' (Apply for leave, check leave balance, cancel leave, casual/earned/sick/comp-off leave)
5. 'timesheet' (Log work hours, submit timesheet, fill timesheet, record project time)
6. 'general' (Greetings, non-work talk, general questions)

Respond ONLY with a valid JSON document containing:
- "intent": the category name (string)
- "confidence": confidence score from 0.0 to 1.0 (float)
- "summary": a short 3-5 word summary of the conversation topic (string)"""

    messages = [{"role": "system", "content": prompt}]
    if history:
        messages.extend(history[-3:])
    messages.append({"role": "user", "content": message})

    try:
        llm_response = await llm.generate_with_history(messages)
        res = llm_response.content
        # Try to parse JSON
        try:
            # handle potential markdown code blocks
            res_clean = res.replace("```json", "").replace("```", "").strip()
            data = json.loads(res_clean)
            if data.get("intent") not in VALID_INTENTS:
                data["intent"] = 'general'
            return data
        except json.JSONDecodeError:
            # Fallback if LLM didn't return proper JSON
            res_lower = res.strip().lower()
            intent = 'general'
            for cat in VALID_INTENTS:
                if cat in res_lower:
                    intent = cat
                    break
            return {
                "intent": intent,
                "confidence": 0.5,
                "summary": message[:30] + "..."
            }
    except Exception as e:
        logger.error(f"Supervisor error: {e}")
        summary = message[:30] + "..." if len(message) > 30 else message
        return {"intent": "general", "confidence": 0.0, "summary": summary}
