# ImpetusAI Workplace Platform — MVP Feature Documentation

**Version:** 0.1.0
**Stack:** FastAPI · LangGraph · LiteLLM · ChromaDB · React/Vite
**Architecture:** Multi-agent RAG system with role-based access control

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [AI Agents](#2-ai-agents)
3. [Core Features](#3-core-features)
4. [Frontend Pages](#4-frontend-pages)
5. [API Reference](#5-api-reference)
6. [Data Models](#6-data-models)
7. [RAG Knowledge Base](#7-rag-knowledge-base)
8. [Configuration & LLM Switching](#8-configuration--llm-switching)
9. [User Roles & Permissions](#9-user-roles--permissions)

---

## 1. System Architecture

```
User (Browser)
    │
    ▼
React Frontend (Vite, port 3000)
    │  Vite proxy /api → 127.0.0.1:8000
    ▼
FastAPI Backend (uvicorn, port 8000)
    │
    ├── JWT Auth Middleware
    ├── SQLite / PostgreSQL  ←── users, conversations, tickets, documents, access_requests
    │
    └── chat_service.py
            │
            ▼
        Supervisor Agent  (classifies intent)
        ┌───────┬──────────┬────────────┐
        ▼       ▼          ▼            ▼
    IT Support  HR Policy  Governance  General
    Agent       Agent      Agent       (LLM direct)
        │           │
        ▼           ▼
    ChromaDB    ChromaDB
    it_runbooks hr_policies
```

### Key Design Decisions

| Decision | Detail |
|----------|--------|
| **LLM abstraction** | All LLM calls go through `ai/llm/gateway.py` (LiteLLM wrapper). Change `LLM_PROVIDER` in `.env` to swap Gemini / Claude / OpenAI / Ollama with zero code changes. |
| **Singleton gateway** | `_gateway` is reset to `None` on every server startup (`main.py`) to pick up fresh `.env` settings. |
| **Async throughout** | FastAPI routes, SQLAlchemy sessions, and all agent calls are fully async. |
| **RAG embeddings** | `all-MiniLM-L6-v2` (SentenceTransformer) — local, no API cost. ChromaDB persisted to `chroma_data/`. |
| **Auto-reload** | uvicorn watches both `backend/` and `ai/` directories (`--reload-dir ../ai`) so agent changes hot-reload without restart. |

---

## 2. AI Agents

### 2.1 Supervisor Agent

**File:** `ai/agents/supervisor.py`
**Purpose:** Routes every user message to the correct specialist agent.

**Flow:**
1. Receives user message + last 3 messages of history
2. Calls LLM with classification prompt
3. Returns `{intent, confidence, summary}`

**Intent Categories:**

| Intent | Triggers | Routes To |
|--------|----------|-----------|
| `it_support` | VPN, hardware, password reset, software issues | IT Support Agent |
| `hr_policy` | Leave, benefits, code of conduct, WFH policy | HR Policy Agent |
| `governance` | Role requests, elevated access, admin rights | Governance Agent |
| `general` | Greetings, non-work conversation | LLM direct response |

**Fallback:** If LLM returns invalid JSON, keyword matching is used. Defaults to `general` with 0.0 confidence.

---

### 2.2 IT Support Agent

**File:** `ai/agents/it_support.py`
**Purpose:** Troubleshoot IT issues and auto-create tickets when needed.

**Key Behaviour:**
- Provides step-by-step resolution guidance
- Detects when an issue requires human intervention
- Embeds `TICKET_REQUIRED` marker + JSON ticket data in its response when a ticket is needed
- Chat service parses this and auto-creates a ticket linked to the conversation

**Ticket auto-creation payload:**
```json
{
  "title": "VPN not connecting",
  "priority": "P2",
  "category": "Network"
}
```

**Priority Scale:** P1 (critical/outage) → P2 (high) → P3 (medium) → P4 (low)
**Categories:** Hardware, Software, Network, Access, Security, General

---

### 2.3 HR Policy Agent

**File:** `ai/agents/hr_policy.py`
**Purpose:** Answer HR questions using policy documents via RAG.

**Flow:**
1. Searches `hr_policies` ChromaDB collection (`top_k=3`)
2. Extracts source filenames, builds context with clean display names
3. Instructs LLM to cite sources by name (e.g., "Leave Policy", "Benefits Policy")
4. Returns response + list of source filenames

**Source links:** Chat service converts filenames to clickable markdown links pointing to `/api/v1/documents/policy/{filename}` (public endpoint, no auth required).

**Pre-loaded demo policies:**
- `leave_policy.md` — Annual leave, sick leave, bereavement, compensatory off
- `benefits_policy.md` — Health insurance, travel reimbursement, allowances
- `code_of_conduct.md` — Workplace behaviour standards
- `remote_work_policy.md` — WFH eligibility, equipment, expectations

---

### 2.4 Governance Agent

**File:** `ai/agents/governance_agent.py`
**Purpose:** Guide users through the access request process.

**Key Behaviour:**
- Explains available roles (employee, hr_admin, it_agent, admin)
- Clarifies that the AI cannot directly grant roles
- Directs users to the Workplace Governance portal in the app
- Requires users to provide a business justification

---

## 3. Core Features

### 3.1 Conversational AI Chat

- Multi-turn conversations with persistent history
- Each conversation auto-titled based on first message
- Conversations can be renamed or deleted (with inline confirmation modal — no browser dialogs)
- Agent tag shown on each AI response (e.g., "HR Policy Agent")
- Suggested prompt chips: "My VPN is not working", "What is the leave policy?", "How to request WFH?"

### 3.2 IT Ticket Management

- Tickets auto-created from chat when IT agent detects an incident
- Manual ticket creation via API
- Full lifecycle: `open → in_progress → waiting → resolved → closed`
- Priority levels P1–P4 with assignment to specific IT agents
- Role-scoped visibility: employees see only their own tickets

### 3.3 HR Policy Q&A with RAG

- Searches indexed policy documents using semantic similarity
- Cites specific source documents in every answer
- Source links open the actual policy file in a new browser tab
- Supports: leave policy, benefits, code of conduct, remote work

### 3.4 Workplace Governance / Access Requests

- Employees can request role elevation (e.g., employee → hr_admin)
- Must provide business justification
- Admins review and approve/reject with optional comments
- On approval: user role is updated automatically in the database
- Duplicate pending requests are blocked

### 3.5 Document Management (Admin/HR Admin)

- Upload HR policies, IT runbooks, SOPs, general docs (PDF, DOCX, MD, TXT)
- Documents are chunked (2048 chars, 200 overlap) and embedded into ChromaDB
- Role-based upload permissions:
  - `admin`: all doc types
  - `hr_admin`: hr_policy only
  - `it_agent`: it_runbook, sop, general
- Max file size: 50MB
- Delete removes both the file and its ChromaDB embeddings

### 3.6 Analytics Dashboard

**Accessible to:** admin, hr_admin, it_agent (role-scoped data)

| Metric | Description |
|--------|-------------|
| Message Volume | All-time, last 7d, last 30d counts |
| Daily Chart | Bar chart of messages per day (last 30 days) |
| Agent Performance | Messages, positive/negative feedback, avg score per agent |
| Ticket Stats | Breakdown by status and priority, avg resolution hours |
| Top Intents | Most frequent intent categories (top 5) |
| User Distribution | By role and department (admin only) |

### 3.7 User Feedback

- Thumbs up / thumbs down on every AI message
- Optional text comment
- Stored per message and aggregated in analytics

### 3.8 User Management (Admin Only)

- View all users with role, department, status
- Create users directly (bypassing self-registration)
- Change user roles
- Suspend / activate accounts

### 3.9 Authentication

- JWT-based, 24-hour token expiry
- Self-registration available (employee role by default)
- Admin bootstrap: first admin auto-created on startup from `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `.env`

---

## 4. Frontend Pages

| Route | Page | Access |
|-------|------|--------|
| `/login` | Login | Public |
| `/signup` | Sign Up | Public |
| `/` | Dashboard | All authenticated |
| `/chat` | AI Chat | All authenticated |
| `/tickets` | IT Tickets | All authenticated |
| `/admin` | Workplace Governance | admin, hr_admin |
| `/admin/users` | User Management | admin only |
| `/analytics` | Analytics Dashboard | admin, hr_admin, it_agent |

---

## 5. API Reference

**Base URL:** `http://localhost:8000/api/v1`
**Swagger UI:** `http://localhost:8000/docs`
**Auth:** Bearer token in `Authorization` header (all protected endpoints)

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | No | Register new user |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/auth/me` | Yes | Current user profile |

### Chat

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/chat/send` | Yes | Send message to AI |
| GET | `/chat/conversations` | Yes | List conversations |
| GET | `/chat/conversations/{id}` | Yes | Get conversation + messages |
| PATCH | `/chat/conversations/{id}` | Yes | Rename conversation |
| DELETE | `/chat/conversations/{id}` | Yes | Delete conversation |
| POST | `/chat/feedback` | Yes | Submit message feedback |

### Tickets

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/tickets` | Yes | Create ticket |
| GET | `/tickets` | Yes | List tickets (role-scoped) |
| GET | `/tickets/{id}` | Yes | Get ticket detail |
| PATCH | `/tickets/{id}` | IT/Admin | Update ticket |

### Documents

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/documents/upload` | Admin/HR/IT | Upload & ingest document |
| GET | `/documents` | Yes | List documents |
| GET | `/documents/policy/{filename}` | **No** | Serve demo policy file |
| DELETE | `/documents/{id}` | Privileged | Delete document |

### Governance

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/governance/request` | Yes | Submit access request |
| GET | `/governance/requests` | Admin/HR | List all requests |
| POST | `/governance/requests/{id}/process` | Admin/HR | Approve or reject |
| GET | `/governance/stats` | Admin/HR | Governance statistics |

### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/users` | Admin | List all users |
| POST | `/admin/users` | Admin | Create user |
| PATCH | `/admin/users/{id}` | Admin | Update role/status |

### Analytics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/analytics/dashboard` | Admin/HR/IT | Full analytics dashboard |

---

## 6. Data Models

### User
```
id, email, hashed_password, full_name, employee_id
department, role, registration_status, is_active
created_at, updated_at
```

### Conversation
```
id, user_id, title, module, status
created_at, updated_at
→ messages[]
```

### Message
```
id, conversation_id, role (user/assistant/system)
content, agent_name, metadata_json
feedback (+1/-1), feedback_comment
created_at
```

### Ticket
```
id, conversation_id (nullable), created_by, assigned_to
title, description, category, subcategory
priority (P1-P4), status, resolution
created_at, updated_at, resolved_at
```

### AccessRequest
```
id, user_id, requested_role, justification
status (pending/approved/rejected)
processed_by, admin_comment
created_at, updated_at
```

### Document
```
id, filename, original_name, file_path, file_size
doc_type, category, description
chunk_count, is_demo, is_indexed
uploaded_by, created_at
```

---

## 7. RAG Knowledge Base

**Vector Store:** ChromaDB (local, `chroma_data/`)
**Embedding Model:** `all-MiniLM-L6-v2` (runs locally, no API key needed)
**Chunking:** 2048 characters, 200 character overlap
**Similarity Threshold:** 0.3 (results below this score are filtered)

### Collections

| Collection | Used By | Content |
|------------|---------|---------|
| `hr_policies` | HR Policy Agent | Leave, benefits, code of conduct, WFH policies |
| `it_runbooks` | IT Support Agent (future) | IT operational runbooks |
| `sops` | General (future) | Standard operating procedures |
| `general_docs` | General (future) | Miscellaneous knowledge |

### Demo Policies (auto-seeded on first startup)

| File | Topics Covered |
|------|----------------|
| `leave_policy.md` | Annual leave (24 days/yr), sick leave, bereavement, public holidays, compensatory off, LWP |
| `benefits_policy.md` | Health insurance, travel reimbursement, allowances |
| `code_of_conduct.md` | Workplace behaviour, ethics standards |
| `remote_work_policy.md` | WFH eligibility, equipment, expectations |

---

## 8. Configuration & LLM Switching

All settings are loaded from `.env` (placed at project root).

### LLM Provider Switch (Single Config Point)

| Provider | `LLM_PROVIDER` | `LLM_MODEL` | API Key Env Var |
|----------|----------------|-------------|-----------------|
| Gemini (default) | `gemini` | `gemini/gemini-2.0-flash` | `GEMINI_API_KEY` |
| Claude | `claude` | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Ollama (local) | `ollama` | `ollama/mistral` | `OLLAMA_BASE_URL` |

### Other Key Settings

```env
DATABASE_URL=sqlite+aiosqlite:///./impetusai.db
SECRET_KEY=<64-char-random-hex>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.3
MAX_UPLOAD_SIZE_MB=50
ADMIN_EMAIL=admin@impetus.com
ADMIN_PASSWORD=ChangeMe123!
```

---

## 9. User Roles & Permissions

| Permission | employee | it_agent | hr_admin | admin |
|------------|----------|----------|----------|-------|
| Use AI chat | ✅ | ✅ | ✅ | ✅ |
| View own tickets | ✅ | ✅ | ✅ | ✅ |
| Update any ticket | ❌ | ✅ | ❌ | ✅ |
| View all tickets | ❌ | ✅ | ❌ | ✅ |
| Upload HR policy docs | ❌ | ❌ | ✅ | ✅ |
| Upload IT runbooks | ❌ | ✅ | ❌ | ✅ |
| View analytics | ❌ | ✅ | ✅ | ✅ |
| Review access requests | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |
| Create users directly | ❌ | ❌ | ❌ | ✅ |

---

## Demo Credentials

| Email | Role | Password |
|-------|------|----------|
| `test@impetus.com` | admin | `ChangeMe123!` |
| `gov_test@impetus.com` | hr_admin | `ChangeMe123!` |
| `demo@gmail.com` | employee | `Demo1234` |

---

*Generated: 2026-03-19 | ImpetusAI MVP v0.1.0*
