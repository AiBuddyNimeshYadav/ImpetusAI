# ImpetusAI MVP Build — Task Tracker

## Phase 1: Backend Core (Sprint 0)
- [x] Create implementation plan and get user approval
- [x] Complete backend API scaffolding ([main.py](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/app/main.py), routers, schemas, services)
- [x] Auth system: signup/login with JWT + bcrypt password hashing
- [x] LLM Gateway: abstract provider (Gemini first, swappable to Ollama/Claude)
- [x] RAG pipeline: document ingestion, chunking, embedding, retrieval
- [x] Demo HR policy documents: create sample Markdown policies for testing

## Phase 2: API Endpoints
- [x] Auth endpoints: `/auth/signup`, `/auth/login`, `/auth/me`
- [x] Chat endpoints: `/chat/send`, `/chat/history`, `/chat/conversations`
- [x] Ticket endpoints: CRUD for IT tickets
- [x] HR Policy Q&A: integrated into chat pipeline via agents
- [x] Document management: upload, list, delete

## Phase 3: AI Agents
- [x] Supervisor agent: intent classification
- [x] IT Support agent: classify IT issues + extract ticket fields
- [x] HR Policy agent: RAG-powered Q&A with citations
- [x] LLM gateway with Gemini integration (LiteLLM)

## Phase 4: Frontend
- [x] Next.js project scaffolding
- [x] Login/Signup pages
- [x] Chat interface
- [x] Ticket dashboard
- [x] Admin panel (document upload)

## Phase 5: Docker Compose
- [x] Dockerfile for backend
- [x] Dockerfile for frontend
- [x] [docker-compose.yml](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/docker-compose.yml) with all services
- [x] Environment configuration ([.env.example](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/.env.example) and fixed [.env](file:///c:/Users/nimes/.gemini/antigravity/playground/perihelion-triangulum/backend/.env) malformation)
- [x] Absolute path resolution for libraries and databases (ChromaDB)

## Phase 6: Verification
- [x] Backend API tests (Intent, RAG, Rename)
- [x] End-to-end flow test (Validated via Mock & API logic audit)
- [x] Docker Compose up and running
- [x] Walkthrough document updated
