# ImpetusAI Workplace Platform — MVP Build Plan

Build a working MVP of the ImpetusAI platform with: email/password auth, AI chat (Gemini-powered), IT ticket creation, HR policy Q&A via RAG, and local Docker Compose deployment. The existing codebase has models, config, and database scaffolding already in place.

## User Review Required

> [!IMPORTANT]
> **Signup data storage**: User credentials (email, password) will be stored in a local SQLite database (upgradable to PostgreSQL). Passwords are hashed with **bcrypt** (never stored in plaintext). JWT tokens are used for session management.

> [!IMPORTANT]
> **HR Policy document upload**: Place your organization's HR policy PDFs/DOCX files in `backend/uploads/hr_policies/`. An admin panel page will also allow drag-and-drop upload. For MVP, demo policy documents will be auto-generated.

> [!IMPORTANT]
> **LLM Swap Point**: All LLM calls go through a single `LLMGateway` class in `backend/app/services/llm_gateway.py`. To switch from Gemini to Ollama or any other model, change **two env vars** in `.env`: `LLM_PROVIDER` and `LLM_MODEL`. No code changes required.

---

## Proposed Changes

### Backend Core Services

Build the remaining backend layer: auth, chat, tickets, HR Q&A, RAG pipeline, and LLM gateway.

#### [MODIFY] [main.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/main.py)
FastAPI application entry point with CORS, startup events (DB init, demo data seeding), and router registration.

#### [NEW] [models/__init__.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/models/__init__.py)
Re-export all models so `Base.metadata.create_all` discovers them.

---

#### [NEW] [schemas/user.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/schemas/user.py)
Pydantic schemas: `UserCreate`, `UserLogin`, `UserResponse`, `Token`.

#### [NEW] [schemas/chat.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/schemas/chat.py)
Pydantic schemas: `ChatRequest`, `ChatResponse`, `ConversationResponse`, `MessageResponse`.

#### [NEW] [schemas/ticket.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/schemas/ticket.py)
Pydantic schemas: `TicketCreate`, `TicketUpdate`, `TicketResponse`.

#### [NEW] [schemas/document.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/schemas/document.py)
Pydantic schemas: `DocumentResponse`, `DocumentUploadResponse`.

---

#### [NEW] [services/auth_service.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/auth_service.py)
- Password hashing with bcrypt
- JWT token creation and verification
- User signup (checks for duplicate email)
- User login (validate credentials, return JWT)

#### [NEW] [services/llm_gateway.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/llm_gateway.py)
- Single abstraction over LiteLLM for all LLM calls
- Reads `LLM_PROVIDER` and `LLM_MODEL` from config
- `generate()` method with prompt + optional system message
- Automatic API key injection based on provider
- **This is the single swap point**: change env vars to switch models

#### [NEW] [services/chat_service.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/chat_service.py)
- Create conversation, send message, get history
- Routes messages through the AI supervisor agent
- Stores messages in DB with agent metadata

#### [NEW] [services/ticket_service.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/ticket_service.py)
- CRUD operations for tickets
- Auto-assign priority/category (called by AI agents)
- List tickets with filters (by user, status, priority)

#### [NEW] [services/rag_service.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/rag_service.py)
- Document ingestion: parse PDF/DOCX → chunk → embed → store in ChromaDB
- Query: embed query → vector search → return relevant chunks
- Uses `sentence-transformers` for local embeddings

#### [NEW] [services/hr_service.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/hr_service.py)
- HR policy Q&A: takes a question, retrieves context via RAG, generates answer with citations using LLM gateway

---

#### [NEW] [api/v1/auth.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/api/v1/auth.py)
- `POST /api/v1/auth/signup` — Register new user
- `POST /api/v1/auth/login` — Login, returns JWT
- `GET /api/v1/auth/me` — Get current user profile

#### [NEW] [api/v1/chat.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/api/v1/chat.py)
- `POST /api/v1/chat/send` — Send message, get AI response
- `GET /api/v1/chat/conversations` — List user's conversations
- `GET /api/v1/chat/conversations/{id}` — Get conversation with messages
- `POST /api/v1/chat/feedback` — Submit feedback on a message

#### [NEW] [api/v1/tickets.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/api/v1/tickets.py)
- `POST /api/v1/tickets` — Create ticket
- `GET /api/v1/tickets` — List tickets (filtered)
- `GET /api/v1/tickets/{id}` — Get ticket detail
- `PATCH /api/v1/tickets/{id}` — Update ticket status

#### [NEW] [api/v1/documents.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/api/v1/documents.py)
- `POST /api/v1/documents/upload` — Upload and ingest a document
- `GET /api/v1/documents` — List uploaded documents
- `DELETE /api/v1/documents/{id}` — Delete a document

#### [NEW] [api/deps.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/api/deps.py)
- `get_current_user` dependency — extracts user from JWT Bearer token

---

### AI Agents

#### [NEW] [services/agents/supervisor.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/agents/supervisor.py)
Intent classifier: routes user messages to IT support, HR policy, or general conversation.

#### [NEW] [services/agents/it_support.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/agents/it_support.py)
Classifies IT issues, extracts ticket fields, decides whether to create ticket or suggest self-service fix.

#### [NEW] [services/agents/hr_policy.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/services/agents/hr_policy.py)
Queries RAG pipeline for HR policies, formats answer with citations.

---

### Demo HR Policy Documents

#### [NEW] [demo_policies/](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/demo_policies/)
Create 3-4 sample HR policy text files for testing RAG:
- `leave_policy.md` — Leave types, annual/sick/casual leave entitlements
- `code_of_conduct.md` — Workplace behavior, dress code, ethics
- `remote_work_policy.md` — WFH guidelines, equipment, expenses
- `benefits_policy.md` — Health insurance, retirement, reimbursements

These are auto-ingested into ChromaDB on first startup. When real policies are available, place PDFs in `backend/uploads/hr_policies/` or use the admin upload endpoint.

---

### Frontend (Next.js)

#### [NEW] [frontend/](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/)
Complete Next.js 14 application with:
- **Login/Signup pages** — Email/password auth connecting to backend JWT
- **Chat interface** — Real-time-like chat with AI, markdown rendering, agent indicators
- **Ticket dashboard** — View, filter, and manage IT tickets
- **Admin panel** — Document upload for HR policies, user management
- **Dark mode** with premium glassmorphism design, smooth transitions

---

### Docker & Deployment

#### [NEW] [docker-compose.yml](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/docker-compose.yml)
Services: `backend` (FastAPI), `frontend` (Next.js), with volumes for uploads and ChromaDB data.

#### [NEW] [backend/Dockerfile](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/Dockerfile)
Python 3.11 slim image with pip install from [pyproject.toml](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/pyproject.toml).

#### [NEW] [frontend/Dockerfile](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/frontend/Dockerfile)
Multi-stage Node.js build with Next.js standalone output.

#### [NEW] [.env.example](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/.env.example)
Template with all required environment variables documented.

---

## Verification Plan

### Automated Tests
1. **Backend startup test**: `cd backend && python -m pytest tests/ -v` — Verify the app starts and models create correctly.
2. **API smoke test** (manual script):
   ```bash
   # Start the backend
   cd backend && pip install -e . && uvicorn app.main:app --port 8000
   
   # Test signup
   curl -X POST http://localhost:8000/api/v1/auth/signup -H "Content-Type: application/json" -d '{"email":"test@impetus.com","password":"Test1234!","full_name":"Test User"}'
   
   # Test login (capture token)
   curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@impetus.com","password":"Test1234!"}'
   
   # Test chat (with token)
   curl -X POST http://localhost:8000/api/v1/chat/send -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"message":"What is the leave policy?"}'
   ```

### Manual Verification
1. **Docker Compose**: Run `docker-compose up --build` from the project root and verify both backend (`:8000`) and frontend (`:3000`) are accessible.
2. **Auth flow**: Sign up on the frontend, log in, verify JWT is stored and API calls work.
3. **Chat**: Send a message in the chat UI and verify AI responds (requires `GEMINI_API_KEY` set in `.env`).
4. **HR Q&A**: Ask "What is the leave policy?" and verify the response cites demo policy documents.
5. **Tickets**: Create an IT issue via chat (e.g., "My VPN is not working") and verify a ticket appears in the dashboard.
