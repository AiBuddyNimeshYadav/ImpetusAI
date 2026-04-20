# End-to-End Implementation Plan

## Project: ImpetusAI Workplace Platform

**Version:** 1.0  
**Date:** March 12, 2026  
**Organization:** Impetus Technologies  

---

## 1. Implementation Strategy

The implementation follows an **Agile-Phased Delivery** model:
- **MVP (Phase 1):** Core platform foundation + IT ticketing + HR Q&A — **16 weeks**
- **Phase 2:** Advanced automation + integrations + knowledge hub — **12 weeks**
- **Phase 3:** Intelligence layer + productization — **12 weeks**

**Total Duration:** ~40 weeks (10 months)

---

## 2. Team Structure

| Role | Count | Responsibilities |
|------|-------|-----------------|
| Tech Lead / Architect | 1 | Architecture decisions, code reviews, LLM strategy |
| Full-Stack Engineer (Backend-heavy) | 2 | FastAPI services, database, integrations |
| Frontend Engineer | 1 | Next.js UI, chatbot interface, dashboards |
| AI/ML Engineer | 2 | Agent design, RAG pipeline, LLM tuning, prompt engineering |
| DevOps / Platform Engineer | 1 | CI/CD, Kubernetes, monitoring, Ollama deployment |
| QA Engineer | 1 | Testing (functional, integration, AI quality) |
| Product Owner / Scrum Master | 1 | Requirements, backlog management, stakeholder sync |
| **Total** | **9** | |

---

## 3. Technology Stack Decision Matrix

### 3.1 Frontend

| Option | Pros | Cons | **Decision** |
|--------|------|------|-------------|
| **Next.js 14 + React 18** | SSR, API routes, great DX, large ecosystem | Heavier than vanilla React | ✅ **Selected** |
| Vite + React | Fast builds, lightweight | No SSR out of box | ❌ |
| Angular | Enterprise-grade, opinionated | Steeper learning curve, smaller AI community | ❌ |

**UI Library:** Shadcn/UI (highly customizable, built on Radix primitives)  
**Styling:** Tailwind CSS  
**Charts:** Recharts or Chart.js  
**Real-time:** Socket.IO  

### 3.2 Backend

| Option | Pros | Cons | **Decision** |
|--------|------|------|-------------|
| **FastAPI (Python)** | Async, auto-docs, best LLM ecosystem (LangChain) | Python concurrency limitations | ✅ **Selected** |
| Flask | Simple, mature | No async, no auto-docs | ❌ |
| Express.js (Node) | Fast, JS ecosystem | Weaker LLM/ML library ecosystem | ❌ |
| Spring Boot (Java) | Enterprise-grade | Heavy, poor LLM ecosystem | ❌ |

**Task Queue:** Celery with Redis broker  
**API Documentation:** FastAPI auto-generated OpenAPI  

### 3.3 AI / LLM Framework

| Option | Pros | Cons | **Decision** |
|--------|------|------|-------------|
| **LangChain + LangGraph** | Best multi-agent support, huge community | Abstraction complexity | ✅ **Selected** |
| AutoGen (Microsoft) | Good multi-agent | Less flexible orchestration | ❌ |
| CrewAI | Simple agent definition | Less mature, fewer tools | ❌ |
| Custom (no framework) | Full control | High development effort | ❌ |

### 3.4 LLM Models

| Use Case | Model | Hosting | Cost (est.) |
|----------|-------|---------|-------------|
| **Sensitive data (HR, PII)** | Mistral 7B Instruct / Llama 3.1 8B | Ollama (on-premise / GPU VM) | $200–400/mo (GPU infra) |
| **Complex reasoning / routing** | Google Gemini 1.5 Pro | API | ~$7/MTok input, $21/MTok output |
| **High-quality fallback** | Anthropic Claude 3.5 Sonnet | API | ~$3/MTok input, $15/MTok output |
| **Embeddings** | all-MiniLM-L6-v2 | Local (CPU) | Free |
| **Reranking** | cross-encoder/ms-marco-MiniLM-L-6-v2 | Local (CPU) | Free |

**LLM Proxy:** LiteLLM — provides unified API, auto-failover, token tracking, cost monitoring

### 3.5 Database

| Type | Technology | Justification |
|------|-----------|---------------|
| **Application Data** | PostgreSQL 16 | ACID compliance, JSON support, mature, free |
| **Vector Store** | ChromaDB (MVP) → Qdrant (Production) | ChromaDB is simple for dev; Qdrant scales better |
| **Cache/Sessions** | Redis 7 | In-memory speed, Pub/Sub for real-time features |
| **Search/Logs** | Elasticsearch 8 | Full-text search, log aggregation |
| **Object Storage** | MinIO (on-prem) / S3 (cloud) | Document and artifact storage |

### 3.6 Infrastructure

| Component | Technology |
|-----------|-----------|
| Containerization | Docker |
| Orchestration | Kubernetes (K3s for dev, EKS/AKS for production) |
| CI/CD | GitHub Actions or GitLab CI |
| IaC | Terraform / Helm Charts |
| Monitoring | Prometheus + Grafana |
| Logging | ELK Stack |
| Auth | Keycloak (open-source IAM) |
| API Gateway | Kong (open-source) |

---

## 4. Phase 1: MVP (Weeks 1–16)

### 4.1 Sprint Breakdown

#### Sprint 0: Foundation (Weeks 1–2)

| Task | Owner | Deliverable |
|------|-------|------------|
| Project setup: mono-repo structure, linting, CI/CD | DevOps + Tech Lead | GitHub repo with CI pipeline |
| Docker Compose for local development | DevOps | `docker-compose.yml` with all services |
| PostgreSQL schema design and migration setup | Backend | Alembic migrations |
| FastAPI boilerplate for all services | Backend | Service scaffolding |
| Next.js project scaffolding with Tailwind + Shadcn | Frontend | UI boilerplate |
| Keycloak setup with LDAP integration | DevOps | SSO working |
| Ollama setup with Mistral 7B | AI/ML | Local LLM serving |
| LiteLLM configuration (Ollama + Gemini) | AI/ML | LLM gateway working |

**Sprint 0 Definition of Done:**
- ✅ All developers can run the full stack locally via `docker-compose up`
- ✅ LLM gateway responds to test prompts
- ✅ SSO login works with test AD user

---

#### Sprint 1–2: Core Chat & IT Ticket Bot (Weeks 3–6)

| Task | Owner | Deliverable |
|------|-------|------------|
| Chat service: WebSocket + message persistence | Backend | Real-time chat API |
| Chat UI: message bubbles, markdown, typing indicator | Frontend | Chat interface component |
| Supervisor Agent: intent classification | AI/ML | Routes to IT/HR agents |
| IT Triage Agent: classify issues | AI/ML | Category + priority output |
| Ticket Creator Agent: extract fields, create ticket | AI/ML | Structured ticket from NL |
| Ticket service: CRUD APIs | Backend | Ticket management endpoints |
| Ticket list + detail views in UI | Frontend | Ticket management UI |

**Sprint 1–2 Definition of Done:**
- ✅ User can chat and describe an IT issue
- ✅ AI classifies the issue and creates a structured ticket
- ✅ Tickets appear in the ticket management dashboard

---

#### Sprint 3–4: Self-Service Resolution & Routing (Weeks 7–10)

| Task | Owner | Deliverable |
|------|-------|------------|
| Self-Service Resolver Agent | AI/ML | Automated L1 resolution attempts |
| Knowledge base seeder (load IT runbooks) | AI/ML | Runbooks indexed in vector DB |
| RAG pipeline for IT knowledge search | AI/ML | Context-aware answers from runbooks |
| Routing Agent + routing rules engine | Backend + AI/ML | Smart ticket routing |
| Routing rules admin interface | Frontend | Admin can configure rules |
| ITSM integration (ServiceNow/Jira SM API) | Backend | Bi-directional ticket sync |

**Sprint 3–4 Definition of Done:**
- ✅ AI attempts to resolve common issues before creating ticket
- ✅ Unresolved tickets are routed to correct team
- ✅ Tickets sync with ITSM tool

---

#### Sprint 5–6: HR Policy Q&A & Onboarding (Weeks 11–14)

| Task | Owner | Deliverable |
|------|-------|------------|
| Document ingestion pipeline (PDF, DOCX parser) | AI/ML | Automated document chunking + embedding |
| HR Policy Agent with RAG | AI/ML | Policy Q&A with citations |
| HR policy document upload interface | Frontend | Admin uploads policy docs |
| Onboarding service: checklist generation API | Backend | Role-based onboarding checklists |
| Onboarding Agnt: dynamic checklist creation | AI/ML | AI-generated onboarding workflows |
| Onboarding portal UI | Frontend | New joiner dashboard |
| Notification service (email) | Backend | Email notifications for tasks |

**Sprint 5–6 Definition of Done:**
- ✅ Employees can ask HR policy questions and get cited answers
- ✅ New joiners see personalized onboarding checklists
- ✅ Task reminders sent via email

---

#### Sprint 7–8: Dashboard, Analytics & Hardening (Weeks 15–16)

| Task | Owner | Deliverable |
|------|-------|------------|
| Admin dashboard: system config, user management | Frontend + Backend | Admin panel |
| Analytics service: ticket metrics, usage stats | Backend | Analytics APIs |
| Analytics dashboard UI | Frontend | Charts and metrics views |
| Feedback mechanism (thumbs up/down) | Frontend + Backend | User feedback collection |
| PII redaction layer integration (Presidio) | AI/ML | PII protection for LLM calls |
| Audit logging across all services | Backend | Compliance-ready logs |
| Security hardening: rate limiting, input validation | DevOps + Backend | Security pass |
| Performance testing (500 concurrent users) | QA | Load test report |
| Bug fixes and polish | All | Production-ready MVP |

**Sprint 7–8 Definition of Done:**
- ✅ Admin can manage system, view analytics
- ✅ PII redaction working for all LLM calls
- ✅ System handles 500 concurrent users
- ✅ All OWASP Top 10 mitigations in place

---

### 4.2 MVP Feature Summary

| Feature | Status |
|---------|--------|
| SSO Login | ✅ MVP |
| AI Chat Interface | ✅ MVP |
| IT Ticket Creation (NL to ticket) | ✅ MVP |
| Ticket Classification & Routing | ✅ MVP |
| Self-Service Resolution | ✅ MVP |
| HR Policy Q&A (RAG) | ✅ MVP |
| Onboarding Checklist | ✅ MVP |
| Admin Dashboard | ✅ MVP |
| Analytics Dashboard | ✅ MVP |
| Feedback Collection | ✅ MVP |
| PII Redaction | ✅ MVP |
| Audit Logging | ✅ MVP |
| ITSM Integration | ✅ MVP |

---

## 5. Phase 2: Advanced Features (Weeks 17–28)

### 5.1 Feature List

| Feature | Sprint | Description |
|---------|--------|-------------|
| **Automated Remediation Engine** | 9–10 | Execute scripts for password reset, VPN fix, etc. |
| **Contextual Escalation** | 9–10 | Human handoff with full AI conversation context |
| **Slack Bot Integration** | 11–12 | Full chatbot experience within Slack |
| **Teams Bot Integration** | 11–12 | Full chatbot experience within MS Teams |
| **Enterprise Knowledge Search** | 13–14 | Semantic search across SOPs, Confluence, SharePoint |
| **Personalized Onboarding Journeys** | 13–14 | Role-specific training paths and content recommendations |
| **HR Document Generation** | 13–14 | Auto-generate offer/confirmation letters from templates |
| **Leave & Benefits Assistant** | 13–14 | HRMS-integrated leave balance + policy bot |
| **Advanced Analytics** | 13–14 | Trend analysis, forecasting, custom reports |
| **Model Fine-tuning Pipeline** | 13–14 | Feedback-driven model improvement |

### 5.2 Key Deliverables
- 🔧 Automated remediation for top 10 common IT issues
- 💬 Slack & Teams bots for company-wide adoption
- 📚 Full enterprise knowledge search across all document sources
- 📝 HR document auto-generation
- 📊 Advanced analytics with trend analysis

---

## 6. Phase 3: Intelligence & Productization (Weeks 29–40)

### 6.1 Feature List

| Feature | Sprint | Description |
|---------|--------|-------------|
| **NMG Network Automation** | 15–16 | Automated network access requests, diagnostics |
| **Predictive Analytics** | 15–16 | Ticket volume forecasting, attrition risk prediction |
| **Knowledge Gap Detection** | 17–18 | Identify FAQ patterns without documentation |
| **Auto Knowledge Capture** | 17–18 | Extract knowledge articles from resolved tickets |
| **Multi-language Support** | 17–18 | Hindi + English bilingual support |
| **Voice Interface** | 19–20 | Voice-to-text for accessibility |
| **Client-Facing Productization** | 19–20 | Multi-tenant architecture, white-label capabilities |
| **AI Governance Dashboard** | 19–20 | LLM audit, bias detection, compliance reporting |

### 6.2 Key Deliverables
- 🔮 Predictive analytics for proactive issue prevention
- 🌐 Multi-language support for global teams
- 🏢 Multi-tenant architecture ready for client deployment
- 📋 AI governance and compliance dashboard

---

## 7. Risk-Based Contingency Planning

| Risk | Contingency | Timeline Impact |
|------|------------|-----------------|
| GPU infrastructure delays | Use Gemini API as primary; defer Ollama to Sprint 3 | Minimal |
| ITSM API limitations | Build abstraction layer; support webhook-based sync | +1 sprint |
| LLM quality below threshold | Increase RAG context; add human-in-the-loop for critical queries | +1 sprint |
| Team ramp-up on LangGraph | Pair programming sessions; start with simpler 2-agent setup | +1 sprint |
| Stakeholder scope changes | Phase-gate approvals; strict change request process | Managed |

---

## 8. Budget Estimate (MVP — Phase 1)

| Category | Monthly Cost | 16-Week Total |
|----------|-------------|--------------|
| Cloud Infrastructure (K8s, VMs, GPU) | $3,000–5,000 | $12,000–20,000 |
| LLM API Costs (Gemini + Claude) | $500–1,500 | $2,000–6,000 |
| Tooling (GitHub, monitoring, etc.) | $500 | $2,000 |
| Team (9 members × 4 months) | Internal | Internal headcount |
| **Total External Cost** | | **$16,000–28,000** |

> [!NOTE]
> Infrastructure costs can be significantly reduced by using on-premise GPU servers if available. LLM API costs scale with usage and can be optimized by maximizing Ollama (local) usage for sensitive workloads.

---

## 9. Success Metrics Tracking

### MVP Launch Metrics (Week 16)

| Metric | Target | Tracking Method |
|--------|--------|----------------|
| IT tickets auto-created | ≥ 100 tickets via AI | Ticket analytics |
| L1 auto-resolution rate | ≥ 40% (growing to 60%) | Resolution analytics |
| HR query accuracy | ≥ 80% (growing to 85%) | Audit sampling |
| System uptime | ≥ 99% | Monitoring alerts |
| User adoption | ≥ 50% of target users | Usage analytics |
| User satisfaction | ≥ 65 NPS | Survey |

### Phase 2 Metrics (Week 28)

| Metric | Target |
|--------|--------|
| L1 auto-resolution rate | ≥ 60% |
| Channel adoption (Slack/Teams) | ≥ 70% of interactions via Slack/Teams |
| Knowledge search accuracy | ≥ 80% top-3 relevance |
| Onboarding cycle time | ≤ 5 business days |

### Phase 3 Metrics (Week 40)

| Metric | Target |
|--------|--------|
| Overall cost reduction (IT+HR ops) | ≥ 25% |
| Predictive accuracy (ticket volume) | ≥ 75% |
| Client deployments | ≥ 2 pilot clients |

---

## 10. Delivery Milestones

```
Week 0   ─── Project Kickoff & Team Onboarding
Week 2   ─── Sprint 0 Complete: Infrastructure Ready ✅
Week 6   ─── Sprint 1-2 Complete: Core Chat + IT Bot ✅
Week 10  ─── Sprint 3-4 Complete: Resolution + Routing ✅
Week 14  ─── Sprint 5-6 Complete: HR Q&A + Onboarding ✅
Week 16  ─── 🚀 MVP LAUNCH (Phase 1 Complete)
Week 20  ─── Remediation Engine + Escalation Live
Week 24  ─── Slack/Teams Bots Live
Week 28  ─── 🚀 Phase 2 Complete
Week 32  ─── NMG Automation + Predictive Analytics
Week 36  ─── Multi-language + Voice Interface
Week 40  ─── 🚀 Phase 3 Complete — Full Platform Live
```

---

## 11. Project Repository Structure

```
impetusai-platform/
├── README.md
├── CLAUDE.md                          # Claude Code project instructions
├── docker-compose.yml
├── .env.example                       # Environment variable template
├── 01-BUSINESS_REQUIREMENTS_DOCUMENT.md
├── 02-SOFTWARE_REQUIREMENTS_SPECIFICATION.md
├── 03-ARCHITECTURE_DOCUMENT.md
├── 04-IMPLEMENTATION_PLAN.md
├── 05-TECHNOLOGY_STACK_COMPARISON.md
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Monolithic app (all pages, routing, auth)
│       ├── api.js                     # API client with JWT auth
│       └── index.css                  # Global styles
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── demo_policies/                 # Seed HR policy documents for RAG
│   │   ├── benefits_policy.md
│   │   ├── code_of_conduct.md
│   │   ├── leave_policy.md
│   │   └── remote_work_policy.md
│   ├── app/
│   │   ├── main.py                    # FastAPI entry — lifespan, DB init, admin bootstrap
│   │   ├── config.py                  # Pydantic settings from .env
│   │   ├── database.py                # SQLAlchemy async engine + session
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── user.py                # User (roles: employee, it_agent, hr_admin, admin)
│   │   │   ├── conversation.py        # Conversation + Message (with feedback, agent_name)
│   │   │   ├── ticket.py              # IT support tickets
│   │   │   ├── document.py            # Uploaded document metadata
│   │   │   └── access_request.py      # Governance access requests
│   │   ├── schemas/                   # Pydantic v2 request/response schemas
│   │   │   ├── user.py                # UserCreate, Token, AdminUserResponse/Create/Update
│   │   │   ├── chat.py                # ChatRequest, ChatResponse
│   │   │   ├── ticket.py              # TicketCreate, TicketResponse
│   │   │   ├── document.py            # DocumentResponse, DocumentUploadResponse
│   │   │   ├── governance.py          # AccessRequest schemas
│   │   │   └── analytics.py           # AnalyticsDashboard, AgentStats, MessageVolume
│   │   ├── services/                  # Business logic layer
│   │   │   ├── auth_service.py        # JWT + bcrypt auth, signup/login
│   │   │   ├── chat_service.py        # Message routing → AI agents, auto-ticketing
│   │   │   ├── ticket_service.py      # Ticket CRUD
│   │   │   └── hr_service.py          # HR-related services
│   │   └── api/                       # API route handlers
│   │       ├── deps.py                # Shared dependencies (get_current_user, get_db)
│   │       └── v1/
│   │           ├── auth.py            # POST /auth/signup, /auth/login, GET /auth/me
│   │           ├── chat.py            # POST /chat/send, GET /chat/conversations
│   │           ├── tickets.py         # CRUD /tickets
│   │           ├── documents.py       # POST /documents/upload (role-scoped)
│   │           ├── governance.py      # Access request management
│   │           ├── admin.py           # GET/POST/PATCH /admin/users (admin only)
│   │           └── analytics.py       # GET /analytics/dashboard (role-scoped)
│   └── tests/
│       └── test_governance.py
├── ai/                                # Standalone AI package (pip install -e .)
│   ├── pyproject.toml
│   ├── agents/
│   │   ├── supervisor.py              # Intent classifier → routes to specialist agents
│   │   ├── it_support.py              # IT triage + self-service resolution + runbook RAG
│   │   ├── hr_policy.py               # HR policy Q&A with RAG citations
│   │   └── governance_agent.py        # Access request handling
│   ├── llm/
│   │   └── gateway.py                 # LLMGateway — LiteLLM wrapper, provider-agnostic
│   └── rag/
│       └── retriever.py               # RAGService — ingest, chunk, embed, search (ChromaDB)
└── scripts/
    └── re_embed.py                    # Re-embed documents after model change
```

---

## 12. Definition of Done (DoD)

### For Each Sprint
- [ ] All user stories implemented and code reviewed
- [ ] Unit tests written (≥ 80% coverage for new code)
- [ ] Integration tests passing
- [ ] No critical or high-severity bugs
- [ ] Documentation updated (API docs, README)
- [ ] Deployed to staging and smoke tested
- [ ] Demo to stakeholders completed

### For MVP Launch
- [ ] All MVP features functional and tested
- [ ] Security audit completed (OWASP Top 10)
- [ ] Performance test passed (500 concurrent users)
- [ ] PII redaction verified
- [ ] Audit logging verified
- [ ] ITSM integration tested with production data
- [ ] User acceptance testing (UAT) sign-off
- [ ] Operations runbook documented
- [ ] Monitoring and alerting configured
- [ ] Rollback procedure documented and tested
