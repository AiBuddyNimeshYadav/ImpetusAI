# MVP Implementation Plan — ImpetusAI Workplace Platform

## Goal

Build a working MVP of the **ImpetusAI Workplace Platform** — an AI-powered internal workplace assistant for Impetus Technologies. The MVP demonstrates two high-impact use cases: **AI IT Service Desk** (ticket creation, classification, self-service resolution) and **HR Policy Q&A** (RAG-based policy answers with citations).

## MVP Scope (What We're Building NOW)

### Core Features
1. **AI Chat Interface** — Unified conversational interface where employees interact with AI
2. **IT Ticket Bot** — Describe issues in natural language → AI creates structured tickets with classification
3. **Self-Service Resolution** — AI searches knowledge base to suggest fixes before creating a ticket
4. **HR Policy Q&A** — Upload HR policy PDFs → AI answers employee policy questions with citations
5. **Ticket Dashboard** — View, filter, and manage IT tickets
6. **Admin Panel** — Upload documents, manage knowledge base, view system stats
7. **Feedback Mechanism** — Thumbs up/down on AI responses

### Future Features (NOT in this MVP)
- Slack/Teams integration → Phase 2
- Automated remediation scripts → Phase 2
- Personalized onboarding workflows → Phase 2
- Enterprise knowledge search → Phase 2
- NMG network automation → Phase 3
- Predictive analytics → Phase 3
- Multi-language support → Phase 3
- Voice interface → Phase 3

---

## User Review Required

> [!IMPORTANT]
> **Questions that need your input before we proceed:**
>
> 1. **LLM Choice**: Should we start with **Ollama (local, free, private)** or **Gemini API (cloud, paid, more powerful)**? I recommend starting with **Gemini API** for faster development and switching to Ollama later for sensitive data.
> 2. **ITSM Integration**: Do you currently use **ServiceNow**, **Jira Service Management**, or another ticketing tool? For MVP we can build a standalone ticket system and add ITSM integration later.
> 3. **HR Policy Documents**: Do you have sample HR policy PDFs/docs we can use for testing the RAG pipeline? If not, I'll create sample policy documents for demo purposes.
> 4. **Authentication**: Should we implement full SSO/LDAP auth for MVP, or start with simple email/password auth and add SSO in Phase 2?
> 5. **Deployment**: Will you run this locally (Docker Compose) or on a cloud server? Docker Compose is recommended for MVP.

---

## Technology Stack (MVP)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 14 + React 18 + TypeScript | SSR, great DX, modern |
| **Styling** | Tailwind CSS + Shadcn/UI | Beautiful, accessible components |
| **Backend** | Python 3.11 + FastAPI | Best AI/ML ecosystem |
| **AI Framework** | LangChain + LangGraph | Multi-agent orchestration |
| **LLM** | Gemini API (primary) + Ollama (optional) via LiteLLM | Flexibility |
| **Vector DB** | ChromaDB | Simple, local, free |
| **App Database** | SQLite (dev) → PostgreSQL (prod) | Start simple, scale later |
| **Task Queue** | Background tasks (FastAPI) | Celery is overkill for MVP |
| **Real-time** | Server-Sent Events (SSE) | Simpler than WebSocket for MVP |

---

## Proposed Changes

### Project Structure

```
perihelion-triangulum/
├── docs/                              # Documentation (already created)
├── backend/                           # Python FastAPI backend
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings & env config
│   │   ├── database.py                # SQLAlchemy setup
│   │   ├── models/                    # DB models
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── ticket.py
│   │   │   └── document.py
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── chat.py
│   │   │   ├── ticket.py
│   │   │   └── auth.py
│   │   ├── api/                       # API routes
│   │   │   ├── chat.py               # Chat endpoints
│   │   │   ├── tickets.py            # Ticket CRUD
│   │   │   ├── documents.py          # Document upload/manage
│   │   │   ├── admin.py              # Admin endpoints
│   │   │   └── auth.py               # Auth endpoints
│   │   ├── services/                  # Business logic
│   │   │   ├── chat_service.py
│   │   │   ├── ticket_service.py
│   │   │   └── document_service.py
│   │   └── ai/                        # AI layer
│   │       ├── agents/
│   │       │   ├── supervisor.py      # Routes to IT/HR agents
│   │       │   ├── it_triage.py       # IT issue classification
│   │       │   ├── ticket_creator.py  # Creates structured tickets
│   │       │   ├── resolver.py        # Searches KB for solutions
│   │       │   └── hr_policy.py       # RAG-based HR Q&A
│   │       ├── orchestrator.py        # LangGraph graph definition
│   │       ├── rag/
│   │       │   ├── ingestion.py       # PDF parsing + chunking
│   │       │   ├── retriever.py       # Vector search
│   │       │   └── embeddings.py      # Embedding generation
│   │       ├── llm_gateway.py         # LiteLLM configuration
│   │       └── prompts/               # System prompts
│   │           ├── supervisor.txt
│   │           ├── it_triage.txt
│   │           ├── ticket_creator.txt
│   │           ├── resolver.txt
│   │           └── hr_policy.txt
│   └── tests/
├── frontend/                          # Next.js frontend
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              # Dashboard
│   │   │   ├── chat/page.tsx         # Chat interface
│   │   │   ├── tickets/page.tsx      # Ticket list
│   │   │   └── admin/page.tsx        # Admin panel
│   │   ├── components/
│   │   │   ├── ui/                   # Shadcn components
│   │   │   ├── chat/                 # Chat components
│   │   │   ├── tickets/              # Ticket components
│   │   │   └── layout/              # Nav, sidebar
│   │   └── lib/
│   │       ├── api.ts                # API client
│   │       └── utils.ts
│   └── public/
├── sample_docs/                       # Sample HR/IT docs for testing
├── docker-compose.yml                 # Local dev environment
├── .env.example                       # Environment variables template
└── README.md                          # Setup & run instructions
```

---

### Component Breakdown

#### Backend — Core API Service

##### [NEW] `backend/app/main.py`
FastAPI application with CORS, middleware, and route registration.

##### [NEW] `backend/app/config.py`
Environment configuration using Pydantic Settings (LLM API keys, DB URL, etc.).

##### [NEW] `backend/app/database.py`
SQLAlchemy async engine + session factory + SQLite for MVP.

##### [NEW] `backend/app/models/` (all files)
SQLAlchemy ORM models for users, conversations, messages, tickets, documents.

##### [NEW] `backend/app/schemas/` (all files)
Pydantic schemas for API request/response validation.

##### [NEW] `backend/app/api/chat.py`
- `POST /api/chat` — Send message, get AI response (with SSE streaming)
- `GET /api/conversations` — List user's conversations
- `GET /api/conversations/{id}` — Get conversation history
- `POST /api/conversations/{id}/feedback` — Submit feedback

##### [NEW] `backend/app/api/tickets.py`
- `GET /api/tickets` — List tickets with filters
- `GET /api/tickets/{id}` — Ticket detail
- `PATCH /api/tickets/{id}` — Update ticket status
- `GET /api/tickets/stats` — Ticket statistics

##### [NEW] `backend/app/api/documents.py`
- `POST /api/documents/upload` — Upload HR/IT documents for RAG
- `GET /api/documents` — List uploaded documents
- `DELETE /api/documents/{id}` — Remove document

##### [NEW] `backend/app/api/auth.py`
- `POST /api/auth/login` — Email/password login (simple JWT for MVP)
- `POST /api/auth/register` — Register user
- `GET /api/auth/me` — Current user profile

---

#### AI Layer — Multi-Agent System

##### [NEW] `backend/app/ai/orchestrator.py`
LangGraph state graph that routes user messages through the agent pipeline:
```
User Message → Supervisor → [IT Triage | HR Policy | Clarification]
                                 ↓              ↓
                        [Resolver | Ticket Creator]  [RAG Answer]
```

##### [NEW] `backend/app/ai/agents/supervisor.py`
Intent classification agent. Determines if query is IT-related, HR-related, or needs clarification.

##### [NEW] `backend/app/ai/agents/it_triage.py`
Classifies IT issues by category (Hardware/Software/Network/Access) and severity (P1–P4). Decides whether to attempt resolution or create ticket.

##### [NEW] `backend/app/ai/agents/resolver.py`
Searches IT knowledge base for solutions. Provides step-by-step troubleshooting.

##### [NEW] `backend/app/ai/agents/ticket_creator.py`
Extracts structured ticket fields from conversation (title, description, category, priority) and creates ticket.

##### [NEW] `backend/app/ai/agents/hr_policy.py`
RAG-based agent that retrieves relevant policy sections and generates cited answers.

##### [NEW] `backend/app/ai/rag/ingestion.py`
Document processing: PDF parsing → text chunking (512 tokens, 50 overlap) → embedding → ChromaDB storage.

##### [NEW] `backend/app/ai/rag/retriever.py`
Vector similarity search against ChromaDB. Returns top-5 chunks with metadata.

##### [NEW] `backend/app/ai/llm_gateway.py`
LiteLLM setup with provider configuration (Gemini primary, Ollama optional).

---

#### Frontend — Next.js Web Application

##### [NEW] `frontend/src/app/page.tsx` — Dashboard
Role-based landing page with quick stats (open tickets, recent conversations, quick actions).

##### [NEW] `frontend/src/app/chat/page.tsx` — Chat Interface
Primary interaction screen with:
- Message bubbles (user/AI), markdown rendering
- Typing indicator during AI processing
- Quick action buttons ("Report IT Issue", "Ask HR Policy", etc.)
- Feedback buttons (thumbs up/down)
- Conversation sidebar

##### [NEW] `frontend/src/app/tickets/page.tsx` — Ticket Management
- Filterable ticket list table
- Ticket detail modal/page
- Status updates

##### [NEW] `frontend/src/app/admin/page.tsx` — Admin Panel
- Document upload for knowledge base
- System statistics
- Recent conversations log

##### [NEW] `frontend/src/components/` — Reusable Components
Chat bubble, ticket card, navigation bar, sidebar, stat cards, etc.

---

## Execution Process

### Step 1: Backend Setup (Sprint 0)
1. Initialize Python project with `pyproject.toml`
2. Set up FastAPI with database models and migrations
3. Create API routes (auth, chat, tickets, documents)
4. Set up LLM gateway with LiteLLM

### Step 2: AI Agent Layer
1. Build LangGraph orchestrator with supervisor agent
2. Implement IT triage + ticket creator agents
3. Implement resolver agent with knowledge search
4. Build RAG pipeline (ingestion + retrieval)
5. Implement HR policy agent

### Step 3: Frontend
1. Scaffold Next.js project with Tailwind + Shadcn/UI
2. Build chat interface with streaming responses
3. Build ticket dashboard
4. Build admin panel with document upload
5. Build landing dashboard

### Step 4: Integration & Polish
1. Connect frontend to backend APIs
2. End-to-end testing
3. Docker Compose for one-command startup
4. README with setup instructions

---

## Verification Plan

### Automated Tests
- **Backend unit tests**: `cd backend && python -m pytest tests/ -v`
  - Test API endpoints return correct status codes and shapes
  - Test ticket CRUD operations
  - Test document upload and ingestion
  - Test agent routing (supervisor correctly classifies intents)

### Manual Verification (Browser)
1. **Start the application**: `docker-compose up` (or `npm run dev` + `uvicorn`)
2. **Chat flow**: Open chat → type "My VPN is not connecting" → verify AI classifies as IT issue → verify ticket is created
3. **HR Q&A flow**: Upload a sample HR policy PDF → ask "What is the leave policy?" → verify cited answer
4. **Ticket dashboard**: Navigate to tickets → verify created tickets appear with correct classification
5. **Admin panel**: Upload a document → verify it appears in the document list → verify RAG search works

### User Manual Testing
- The user should test with real IT issue descriptions and HR policy documents to evaluate AI quality
- Test in the browser at `http://localhost:3000` after starting with Docker Compose
