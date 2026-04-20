# ImpetusAI Workplace Platform

AI-powered IT Service Desk & HR Assistant for Impetus Technologies.

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Gemini API key ([Get one free](https://aistudio.google.com/apikey))

### 1. Backend Setup

```bash
cd backend

# Create .env from template
cp ../.env.example .env
# Edit .env and add your GEMINI_API_KEY

# Install dependencies
pip install -e ".[dev]"

# Start the backend
uvicorn app.main:app --reload --port 8000
```

Backend will be running at http://localhost:8000 (Swagger UI at http://localhost:8000/docs)

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend will be running at http://localhost:3000

### 3. Docker Compose (Alternative)

```bash
# Copy and configure .env
cp .env.example backend/.env
# Edit backend/.env with your GEMINI_API_KEY

# Build and run
docker-compose up --build
```

## Architecture

```text
┌────────────────┐     ┌───────────────────────────────────┐
│   Frontend     │────▶│   Backend (FastAPI)                │
│   React+Vite   │     │   ├── Auth (JWT + bcrypt)          │
│   Port 3000    │     │   ├── Tickets & Documents APIs     │
└────────────────┘     │   └── Chat Endpoint                │
                       └───────────────────────────────────┘
                                 │
                       ┌───────────────────────────────────┐
                       │   AI Module (Core Intelligence)    │
                       │   ├── Agents (IT, HR, Supervisor)  │
                       │   ├── RAG Retriever & Ingestion    │
                       │   └── LLM Gateway (LiteLLM)        │
                       └───────────────────────────────────┘
```

## Changing LLM & Embedding Models

The system is designed to allow swapping the LLM and Embedding models independently. Edit `backend/.env`:

| Provider | `LLM_PROVIDER` | `LLM_MODEL` | `EMBEDDING_MODEL`
|----------|----------------|-------------|----------------------------|
| Gemini (default) | `gemini` | `gemini/gemini-2.0-flash` | `all-MiniLM-L6-v2` |
| Ollama (local) | `ollama` | `ollama/mistral` | `nomic-embed-text` |

**Important: If you change your Embedding Model, you MUST re-embed all documents.**
A script is provided to automate this process:
```bash
cd backend
python ../scripts/re_embed.py
```

## HR Policy Documents

Place your organization's policy files in: `backend/uploads/hr_policies/`

Or use the Admin panel at http://localhost:3000/admin to upload via the web UI.

Demo policies are auto-loaded from `backend/demo_policies/` on first startup.
