# Comprehensive Testing & Verification Plan

This plan outlines the steps to verify the fix for reported issues: HR knowledge base errors, incorrect agent tagging ("general"), and chat rename failures.

## 1. System Health Audit (Manual)
Run the following script to audit the RAG database and LLM connectivity.
```bash
cd backend
$env:PYTHONPATH="."
python -c "
import asyncio, os
from app.config import get_settings
from ai.rag.retriever import get_rag_service
from ai.llm.gateway import get_llm_gateway

async def audit():
    settings = get_settings()
    print(f'--- Config ---')
    print(f'LLM Provider: {settings.LLM_PROVIDER}')
    print(f'Embeddings Model: {settings.EMBEDDING_MODEL}')
    print(f'Chroma Dir: {os.path.abspath(settings.CHROMA_PERSIST_DIR)}')
    
    print(f'\n--- RAG Check ---')
    rag = get_rag_service()
    col = rag.get_collection('hr_policies')
    count = col.count()
    print(f'HR Policies Collection Count: {count}')
    if count == 0:
        print('![WARNING] Collection is empty. Re-seeding...')
        rag.ingest_demo_policies('demo_policies')
        print(f'New Count: {col.count()}')
    
    print(f'\n--- LLM Check ---')
    llm = get_llm_gateway()
    try:
        res = await llm.generate('Hello, are you linked to the ImpetusAI system?')
        print(f'LLM Response: {res.content[:50]}...')
    except Exception as e:
        print(f'![ERROR] LLM Failed: {e}')

asyncio.run(audit())
"
```

## 2. API Integration Tests
We will perform functional testing of the core endpoints using `curl` or a test script.

### Test A: Intent Classification & Routing
- **Input**: "What is the leave policy?"
- **Expected**: 
  - [intent](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/ai/agents/supervisor.py#7-52) = [hr_policy](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/hr_service.py#8-18)
  - Response contains numbers from [demo_policies/leave_policy.md](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/demo_policies/leave_policy.md) (e.g., 12 days casual, 15 days privileged).
  - `agent_name` in JSON response = [hr_policy](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/hr_service.py#8-18).

### Test B: Chat Renaming
- **Input**: `PATCH /api/v1/chat/conversations/{id}` with `{"title": "Renamed Chat"}`.
- **Expected**: `200 OK` and the title updates in subsequent `GET` calls.

### Test C: IT Support Routing
- **Input**: "My VPN is broken"
- **Expected**: [intent](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/ai/agents/supervisor.py#7-52) = `it_support`.

## 3. Frontend UI Validation
Since the browser tool is currenty hitting protocol errors, we will perform "Code-Driven Proof of UI Correctness" by reviewing the React state transitions in [App.jsx](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/src/App.jsx).

### Rename Implementation Check
- [ ] [startEdit](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/src/App.jsx#241-246) correctly populates `editTitle` and `editingConvId`.
- [ ] [saveEdit](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/src/App.jsx#247-257) nullifies `editingConvId` *before* the async call to prevent double-firing.
- [ ] [saveEdit](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/src/App.jsx#247-257) updates the [conversations](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/chat_service.py#162-170) list in-place via `setConversations` so the UI updates without a page refresh.
- [ ] `onBlur` and `onKeyDown` handlers are mapped to the new [saveEdit](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/src/App.jsx#247-257) signature.

## 4. Success Criteria
- [ ] Auditor script shows >0 chunks in `hr_policies`.
- [ ] AI Chat responses show the correct agent tag ([hr_policy](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/hr_service.py#8-18) or `it_support`).
- [ ] Conversation titles in the sidebar are relevant summaries, not "Error".
- [ ] Renaming a chat via the UI results in an immediate reflection in the sidebar.
