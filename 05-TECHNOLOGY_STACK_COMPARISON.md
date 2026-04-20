# Technology Stack & LLM Model Comparison

## Project: ImpetusAI Workplace Platform

**Version:** 1.0  
**Date:** March 12, 2026  

---

## 1. LLM Model Comparison

### 1.1 Open-Source Models (Self-Hosted via Ollama)

| Model | Parameters | Context Window | Strengths | Weaknesses | GPU Required | **Recommendation** |
|-------|-----------|---------------|-----------|------------|-------------|-------------------|
| **Mistral 7B Instruct** | 7B | 32K | Fast inference, good instruction-following, strong for classification | Limited complex reasoning | 8GB VRAM (RTX 4070+) | ✅ **Primary local model** |
| **Llama 3.1 8B Instruct** | 8B | 128K | Large context, Meta's latest, multilingual | Slightly slower than Mistral 7B | 10GB VRAM | ✅ **Alternative for long context** |
| **Llama 3.1 70B** | 70B | 128K | Excellent reasoning, near-GPT-4 quality | Requires A100/H100 GPU | 40GB+ VRAM | ⚠️ Phase 3 (if GPU available) |
| **Phi-3 Mini** | 3.8B | 128K | Ultra-fast, efficient for simple tasks | Lower quality for complex queries | 4GB VRAM | ⚠️ For edge/lightweight tasks |
| **Qwen2.5 7B** | 7B | 32K | Strong Chinese + English bilingual | Less proven for enterprise use | 8GB VRAM | ❌ Not needed for Impetus |
| **Gemma 2 9B** | 9B | 8K | Google-quality, efficient | Smaller context window | 10GB VRAM | ⚠️ Future evaluation |

### 1.2 API-Based Models

| Model | Provider | Context Window | Cost (per MTok) | Strengths | Weaknesses | **Recommendation** |
|-------|----------|---------------|-----------------|-----------|------------|-------------------|
| **Gemini 1.5 Pro** | Google | 1M tokens | $7 in / $21 out | Massive context, multimodal, great reasoning | Vendor lock-in | ✅ **Primary API model** |
| **Gemini 1.5 Flash** | Google | 1M tokens | $0.075 in / $0.30 out | Ultra-cheap, fast | Lower quality than Pro | ✅ **Bulk/simple tasks** |
| **Claude 3.5 Sonnet** | Anthropic | 200K | $3 in / $15 out | Excellent reasoning and safety | Higher output cost | ✅ **Fallback / high-quality tasks** |
| **Claude 3.5 Haiku** | Anthropic | 200K | $0.25 in / $1.25 out | Very fast and cheap | Less nuanced than Sonnet | ⚠️ For simple routing |
| **GPT-4o** | OpenAI | 128K | $2.50 in / $10 out | Versatile, large ecosystem | OpenAI data policies | ❌ Not recommended (data concerns) |
| **GPT-4o Mini** | OpenAI | 128K | $0.15 in / $0.60 out | Cheapest capable model | OpenAI data policies | ❌ Not recommended |

### 1.3 Recommended LLM Strategy

```
┌─────────────────────────────────────────────────────────┐
│                   LLM Gateway (LiteLLM)                 │
├──────────────────┬──────────────────┬───────────────────┤
│  SENSITIVE DATA  │  GENERAL TASKS   │  COMPLEX TASKS    │
│                  │                  │                    │
│  Ollama Local    │  Gemini Flash    │  Gemini Pro        │
│  Mistral 7B     │  (cheap & fast)  │  (high quality)    │
│                  │                  │                    │
│  PII-containing  │  Routing,        │  Complex reasoning,│
│  HR queries,     │  classification, │  document analysis,│
│  employee data   │  simple Q&A      │  report generation │
├──────────────────┴──────────────────┴───────────────────┤
│  FALLBACK: Claude 3.5 Sonnet (if Gemini is down)       │
└─────────────────────────────────────────────────────────┘
```

### 1.4 Embedding Models Comparison

| Model | Dimensions | Speed | Quality | Cost | **Decision** |
|-------|-----------|-------|---------|------|-------------|
| **all-MiniLM-L6-v2** | 384 | Very Fast | Good | Free (local) | ✅ **MVP** |
| **all-mpnet-base-v2** | 768 | Fast | Better | Free (local) | ⚠️ Phase 2 upgrade |
| **text-embedding-3-small** | 1536 | Fast | Excellent | $0.02/MTok | ⚠️ If local is insufficient |
| **nomic-embed-text** | 768 | Fast | Good | Free (Ollama) | ⚠️ Alternative |

---

## 2. Framework Comparison

### 2.1 AI Orchestration Frameworks

| Framework | Multi-Agent | State Mgmt | Graph-Based | Community | Learning Curve | **Decision** |
|-----------|------------|------------|------------|-----------|---------------|-------------|
| **LangGraph** | ✅ Excellent | ✅ Built-in | ✅ Yes | Large | Medium | ✅ **Selected** |
| AutoGen | ✅ Good | ⚠️ Basic | ❌ No | Growing | Medium | ❌ |
| CrewAI | ✅ Simple | ⚠️ Basic | ❌ No | Small | Low | ❌ |
| Semantic Kernel | ✅ Good | ✅ Good | ❌ No | Microsoft | High | ❌ |
| Custom | ✅ Full control | Build yourself | Optional | N/A | Very High | ❌ |

**Why LangGraph?**
- Native support for **stateful, graph-based** multi-agent workflows
- Built-in **human-in-the-loop** capabilities
- Seamless integration with **LangChain tools** and **LangSmith observability**
- Active development by a well-funded team (LangChain Inc.)
- Large community with extensive examples for enterprise use cases

### 2.2 Backend Frameworks

| Framework | Language | Async | Auto Docs | ML Ecosystem | Performance | **Decision** |
|-----------|----------|-------|-----------|-------------|-------------|-------------|
| **FastAPI** | Python | ✅ | ✅ OpenAPI | ✅ Best | High | ✅ **Selected** |
| Flask | Python | ⚠️ | ❌ | ✅ Good | Medium | ❌ |
| Django | Python | ⚠️ | Plugin | ✅ Good | Medium | ❌ |
| Express.js | Node.js | ✅ | Plugin | ⚠️ Limited | High | ❌ |
| Spring Boot | Java | ✅ | Plugin | ❌ Poor | Very High | ❌ |
| Go (Gin/Fiber) | Go | ✅ | Plugin | ❌ Poor | Very High | ❌ |

### 2.3 Frontend Frameworks

| Framework | SSR | TypeScript | Component Lib | DX | Bundle Size | **Decision** |
|-----------|-----|-----------|--------------|-----|-------------|-------------|
| **Next.js 14** | ✅ | ✅ | Shadcn/UI | Excellent | Optimized | ✅ **Selected** |
| Vite + React | ❌ | ✅ | Any | Good | Small | ❌ |
| Angular | ✅ | ✅ | Material | Good | Large | ❌ |
| Vue + Nuxt | ✅ | ✅ | Vuetify | Good | Medium | ❌ |

### 2.4 Vector Databases

| Database | Cloud/Self-Host | Filtering | Scale | Ease of Setup | Cost | **Decision** |
|----------|----------------|-----------|-------|-------------- |------|-------------|
| **ChromaDB** | Self-Host | Basic | Small-Med | ✅ Very Easy | Free | ✅ **MVP** |
| **Qdrant** | Both | Advanced | Large | ✅ Easy | Free (self-host) | ✅ **Production** |
| Pinecone | Cloud only | Advanced | Large | ✅ Easy | $70+/mo | ❌ (cost + data egress) |
| Weaviate | Both | Advanced | Large | ⚠️ Medium | Free (self-host) | ⚠️ Alternative |
| Milvus | Self-Host | Advanced | Very Large | ⚠️ Complex | Free | ❌ (overkill for MVP) |
| pgvector | Self-Host | Basic | Medium | ✅ Easy | Free | ⚠️ Fallback |

---

## 3. Open-Source Tools Stack

| Category | Tool | Purpose | License |
|----------|------|---------|---------|
| **LLM Serving** | Ollama | Local LLM inference server | MIT |
| **LLM Proxy** | LiteLLM | Unified API for multiple LLM providers | MIT |
| **RAG Framework** | LangChain | Document loading, chunking, retrieval | MIT |
| **Agent Framework** | LangGraph | Multi-agent orchestration | MIT |
| **Observability** | LangSmith (free tier) | LLM tracing and debugging | Freemium |
| **PII Protection** | Microsoft Presidio | PII detection and anonymization | MIT |
| **Auth** | Keycloak | Identity and access management | Apache 2.0 |
| **API Gateway** | Kong | API routing, rate limiting | Apache 2.0 |
| **Task Queue** | Celery | Background job processing | BSD |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards | Apache 2.0 |
| **Logging** | ELK Stack | Centralized logging | Elastic / Apache |
| **Container** | Docker + K8s | Containerization and orchestration | Apache 2.0 |
| **DB Migration** | Alembic | PostgreSQL schema migrations | MIT |
| **Testing** | Pytest + Playwright | Backend + E2E testing | MIT / Apache |
| **Code Quality** | Ruff + mypy | Python linting + type checking | MIT |
| **Doc Parsing** | Unstructured.io | PDF/DOCX parsing for RAG | Apache 2.0 |

---

## 4. Infrastructure Cost Comparison

### 4.1 Cloud Options

| Provider | GPU VM (Ollama) | K8s Cluster (5 nodes) | Managed DB | Total/Month |
|----------|----------------|----------------------|-----------|-------------|
| **AWS** | g5.xlarge ($1,006) | EKS + t3.large ($730) | RDS ($200) | ~$2,000 |
| **Azure** | NC4as T4 ($930) | AKS + D2s ($680) | Flexible Server ($180) | ~$1,800 |
| **GCP** | g2-standard-4 ($890) | GKE + e2-standard-2 ($650) | Cloud SQL ($170) | ~$1,700 |
| **On-Premise** | RTX 4090 ($1,600 one-time) | K3s (existing servers) | Self-managed ($0) | ~$200 (power) |

> [!TIP]
> **Recommendation for Impetus:** Start with **on-premise** or **company-owned servers** for Ollama (saves ~$1K/month on GPU). Use **GCP** for K8s and managed services (best AI/ML ecosystem, Gemini API integration). Consider **spot instances** for non-production environments to reduce costs by 60-70%.

### 4.2 Monthly LLM API Cost Projections

| Usage Level | Gemini Flash | Gemini Pro | Claude Sonnet | Ollama | **Total** |
|-------------|-------------|-----------|---------------|--------|-----------|
| Light (1K employees, 100 queries/day) | $15 | $50 | $20 | $0* | ~$85 |
| Medium (3K employees, 500 queries/day) | $75 | $250 | $100 | $0* | ~$425 |
| Heavy (5K+ employees, 1000 queries/day) | $150 | $500 | $200 | $0* | ~$850 |

*Ollama cost is infrastructure only (included in cloud/on-prem costs above)

---

## 5. Build vs. Buy Analysis

| Component | Build | Buy/SaaS | **Decision** |
|-----------|-------|----------|-------------|
| AI Chat Engine | Custom agents with LangGraph | Dialogflow / Amazon Lex | ✅ **Build** (more control, IP creation) |
| Ticket System | Custom + ITSM integration | ServiceNow AI | ✅ **Build + Integrate** (leverage existing ITSM) |
| RAG Pipeline | LangChain + Vector DB | Cohere RAG / Amazon Kendra | ✅ **Build** (data stays local, customizable) |
| Authentication | Keycloak | Auth0 / Okta | ✅ **Build** (Keycloak is free, full control) |
| Monitoring | Prometheus/Grafana | Datadog / New Relic | ✅ **Build** (open-source, no per-host fees) |
| LLM Serving | Ollama | Hugging Face Endpoints | ✅ **Build** (data sovereignty, one-time GPU cost) |

> [!IMPORTANT]
> **Rationale:** Building the core AI components creates **reusable IP** that Impetus can offer to clients. Using open-source tools keeps costs low while maintaining full control over data and customization. External ITSM and HRMS systems are **integrated, not replaced**, minimizing disruption.
