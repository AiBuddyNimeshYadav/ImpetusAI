# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ImpetusAI Workplace Platform** — An AI-powered IT Service Desk & HR Assistant for enterprise use. It uses a multi-agent architecture (LangGraph + LiteLLM) to route user messages to specialized agents (IT Support, HR Policy, Governance).

## Development Commands

### Backend (FastAPI)
```bash
cd backend
pip install -e ".[dev]"                        # Install with dev deps (pytest, ruff)
uvicorn app.main:app --reload --port 8000      # Dev server with auto-reload
pytest                                          # Run all tests
pytest tests/test_governance.py                # Run a single test file
ruff check app/                                # Lint
ruff format app/                               # Auto-format (line length: 100)
```

### AI Module
```bash
cd ai
pip install -e .                               # Install as editable package
pytest                                          # Run AI module tests
```

### Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev                                    # Dev server on port 3000
npm run build                                  # Production build → dist/
```

### Docker
```bash
docker-compose up --build                      # All services (backend:8000, frontend:3000)
```

### Utilities
```bash
cd backend && python ../scripts/re_embed.py    # Re-embed documents after model change
```

## Environment Setup

Copy `.env.example` to `.env` in the `backend/` directory. The key variable is `LLM_PROVIDER` — changing it (along with `LLM_MODEL` and the matching API key) switches the entire platform to a different LLM:

| Provider | `LLM_PROVIDER` | `LLM_MODEL` |
|----------|----------------|-------------|
| Gemini (default) | `gemini` | `gemini/gemini-2.0-flash` |
| Ollama (local) | `ollama` | `ollama/mistral` |
| Claude | `claude` | `claude-3-5-sonnet-20241022` |
| OpenAI | `openai` | `gpt-4o-mini` |

## Architecture

### Request Flow
```
User → Frontend (React) → FastAPI Backend → chat_service.py
                                                ↓
                                       Supervisor Agent (classifies intent)
                                       ↙        ↓        ↘
                               IT Support   HR Policy  Governance
                               Agent        Agent       Agent
                                  ↓             ↓
                              RAGService    RAGService
                              (ChromaDB)   (ChromaDB)
```

### Key Modules

**`backend/app/`** — FastAPI application
- `main.py` — Entry point; registers all routes, runs DB init + demo policy seeding on startup
- `config.py` — All settings loaded from `.env` via Pydantic (single source of truth for env vars)
- `services/chat_service.py` — Core message routing: calls Supervisor agent, delegates to specialized agents, persists conversation history, auto-creates IT tickets

**`ai/`** — Standalone Python package for all AI logic
- `llm/gateway.py` — `LLMGateway`: unified LiteLLM wrapper; injects correct API keys based on `LLM_PROVIDER`. **All LLM calls go through here.**
- `rag/retriever.py` — `RAGService`: ingests PDF/DOCX/MD → chunks → embeds → stores in ChromaDB; similarity search with score threshold
- `agents/supervisor.py` — Classifies user intent into: `it_support`, `hr_policy`, `governance`, `general`
- `agents/it_support.py` — IT triage, self-service resolution steps, runbook retrieval
- `agents/hr_policy.py` — HR Q&A with RAG over policy documents
- `agents/governance_agent.py` — Access request handling

**`frontend/src/`**
- `App.jsx` — Monolithic component (~1000 lines); contains all pages: Auth, Chat UI, Ticket panel, Admin, Document upload
- `api.js` — Fetch wrapper that injects JWT `Authorization` headers

### Data Stores
- **SQLite** (dev) / **PostgreSQL** (prod): users, conversations, messages, tickets, documents, access_requests
- **ChromaDB** (`./chroma_data/`): vector collections — `hr_policies`, `it_runbooks`, `knowledge_base`, `sops`, `general_docs`

### API Structure
All endpoints are under `/api/v1/`. Auto-docs available at `http://localhost:8000/docs`.
- `POST /api/v1/chat/send` — Main chat endpoint; returns `agent_name`, optionally `ticket_id` if auto-created
- `POST /api/v1/auth/login` — Returns JWT access token
- `POST /api/v1/documents/upload` — Ingest a document into ChromaDB

## Code Conventions

- Python target: **3.11+**; uses `async`/`await` throughout (SQLAlchemy async sessions, async FastAPI routes)
- Ruff rules in effect: `E, F, I, W` — run `ruff check` before committing
- Backend uses **dependency injection** via `backend/app/api/deps.py` for auth (`get_current_user`) and DB sessions
- Pydantic v2 is used for all request/response schemas in `backend/app/schemas/`
- The `ai/` package is imported by the backend as a dependency — changes there affect the backend directly when installed with `pip install -e`
