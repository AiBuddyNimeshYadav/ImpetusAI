# Business Requirements Document (BRD)

## Project: ImpetusAI Workplace Platform

**Organization:** Impetus Technologies  
**Version:** 1.0  
**Date:** March 12, 2026  
**Prepared by:** AI Strategy & Engineering Team  

---

## 1. Executive Summary

Impetus Technologies aims to build an **AI-First Digital Workplace Platform** (codename: **ImpetusAI**) leveraging Generative AI and Multi-Agent architectures to transform internal operations. Inspired by industry leaders like Infosys Topaz, this platform will automate and enhance:

- **IT Service Desk** — Intelligent ticket creation, routing, and self-service resolution
- **HR Operations** — Hyper-personalized onboarding and policy query resolution
- **Knowledge Management** — Enterprise-wide knowledge search and contextual answers

The initiative positions Impetus Technologies as an innovator in the IT services landscape, reducing operational overhead, improving employee experience, and demonstrating AI capabilities to clients.

---

## 2. Business Objectives

| # | Objective | Measurable Target |
|---|-----------|-------------------|
| O1 | Reduce IT ticket resolution time | 40% reduction in mean-time-to-resolution (MTTR) |
| O2 | Automate tier-1 IT support | 60% of L1 tickets auto-resolved without human intervention |
| O3 | Accelerate employee onboarding | Reduce onboarding cycle from 2 weeks to 3 days |
| O4 | Improve HR query response time | 90% of policy queries answered in < 30 seconds |
| O5 | Cut operational costs | 25% reduction in IT helpdesk & HR operations cost |
| O6 | Build reusable AI IP | Create a platform that can be offered as a solution to clients |

---

## 3. Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| CTO / VP Engineering | Executive Sponsor | Strategic alignment, budget approval |
| IT Service Desk Manager | Primary User | Ticket automation, reduced workload |
| HR Director | Primary User | Onboarding automation, policy management |
| NMG (Network Management Group) | Primary User | Infrastructure issue routing |
| Engineering Teams | Secondary Users | Self-service IT resolution |
| CISO / Security Team | Governance | Data privacy, compliance |
| Client Solutions Team | Business Development | Productization for client offerings |

---

## 4. Business Problem Statement

### Current Challenges

1. **IT Service Desk Overload**
   - High volume of repetitive L1 tickets (password resets, VPN issues, software requests)
   - Manual ticket categorization leads to misrouting and delayed resolution
   - Average resolution time for L1 tickets is 4–8 hours
   - NMG team spends 30% of time on routine network access requests

2. **HR Operations Bottleneck**
   - Onboarding involves 12+ manual touchpoints across 5 departments
   - New joiners wait days for responses to basic policy questions
   - HR team handles 200+ repetitive policy queries per month
   - No centralized, searchable knowledge base for company policies

3. **Knowledge Silos**
   - Institutional knowledge locked in individual emails and chat histories
   - Employees waste 2+ hours/week searching for internal information
   - No intelligent search across SOPs, runbooks, and policy documents

---

## 5. Proposed Solution Overview

**ImpetusAI** is a multi-agent GenAI platform composed of three integrated modules:

### Module 1: AI IT Service Desk (AITSD)
- **Smart Ticket Creation** — AI extracts issue details from natural language descriptions
- **Intelligent Routing** — Multi-agent system classifies, prioritizes, and routes tickets
- **Self-Service Resolution** — AI agent attempts automated resolution before escalation
- **Escalation Intelligence** — Context-rich handoff to human agents when needed

### Module 2: AI HR Assistant (AIHRA)
- **Personalized Onboarding** — Dynamic onboarding workflows tailored per role/department
- **Policy Q&A** — RAG-based conversational interface for HR policies
- **Document Generation** — Auto-generate offer letters, confirmation letters, etc.
- **Leave & Benefits Helper** — Automated leave policy clarification and benefits lookup

### Module 3: Enterprise Knowledge Hub (EKH)
- **Unified Search** — Semantic search across all internal documents and SOPs
- **Contextual Answers** — AI-generated answers with source citations
- **Knowledge Capture** — Automatic extraction of knowledge from resolved tickets

---

## 6. Scope

### In Scope (MVP — Phase 1)
- IT Service Desk chatbot with ticket creation and basic auto-routing
- HR Policy Q&A with RAG over policy documents
- Basic onboarding checklist automation
- User authentication via existing SSO/LDAP
- Admin dashboard for monitoring and analytics
- Integration with existing ITSM tool (ServiceNow / Jira Service Management)

### In Scope (Phase 2)
- Multi-agent ticket resolution with automated remediation
- Personalized onboarding workflows
- Enterprise knowledge search across SOPs and runbooks
- Slack/Teams integration
- Feedback loop and model fine-tuning

### In Scope (Phase 3)
- NMG network issue automation
- Predictive analytics (ticket volume forecasting, attrition risk)
- Client-facing productization
- Multi-language support
- Voice-based interaction

### Out of Scope
- Replacement of existing HRMS/ITSM systems (integration only)
- Customer-facing support (external clients)
- Financial or payroll processing automation
- Hardware procurement automation

---

## 7. Success Criteria

| Criteria | Target | Measurement Method |
|----------|--------|--------------------|
| L1 ticket auto-resolution rate | ≥ 60% | Ticket system analytics |
| Average ticket routing accuracy | ≥ 90% | Routing audit sampling |
| HR query response accuracy | ≥ 85% | User feedback + manual audit |
| Employee satisfaction (NPS) | ≥ 70 | Quarterly survey |
| Onboarding completion time | ≤ 3 business days | HR process tracking |
| System availability | ≥ 99.5% | Infrastructure monitoring |
| Cost reduction (IT + HR ops) | ≥ 25% | Finance department metrics |

---

## 8. Assumptions

1. Impetus Technologies has existing SSO/LDAP infrastructure for authentication
2. IT and HR policy documents are available in digital formats (PDF, Word, Confluence)
3. An existing ITSM tool (ServiceNow or Jira Service Management) is in use
4. A communication platform (Slack or Microsoft Teams) is deployed org-wide
5. Budget is approved for cloud GPU instances or API-based LLM costs
6. Data privacy regulations (internal + GDPR if applicable) will be adhered to
7. Internal stakeholders will provide domain expertise for agent training

---

## 9. Constraints

1. **Data Privacy** — All employee data must stay within organizational boundaries; no PII sent to external APIs unless encrypted/anonymized
2. **Budget** — MVP must be delivered within a $50K–$100K budget envelope
3. **Timeline** — MVP must be production-ready within 16 weeks
4. **Compliance** — Must comply with ISO 27001 and SOC2 requirements of Impetus
5. **Model Choice** — Preference for open-source models (Ollama/local) for sensitive data; API-based (Gemini/Claude) for non-sensitive workloads

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| LLM hallucination in HR policy answers | High | Medium | RAG with citation + human review for critical queries |
| Data leakage to external LLM APIs | Critical | Low | On-premise Ollama for sensitive data; API gateway with PII redaction |
| Low user adoption | High | Medium | Phased rollout, champion users, gamification |
| Integration complexity with legacy ITSM | Medium | High | API-first design; use webhooks as fallback |
| Model performance degradation over time | Medium | Medium | Continuous monitoring + feedback loop + periodic retraining |
| Scope creep | Medium | High | Strict phase-gating and stakeholder sign-off |

---

## 11. Regulatory & Compliance Requirements

- **ISO 27001** — Information security management
- **SOC 2 Type II** — Service organization controls for data handling
- **GDPR** (if applicable) — Data protection for EU employees
- **India IT Act / DPDPA 2023** — Digital Personal Data Protection Act compliance
- **Internal Audit** — Quarterly AI governance review

---

## 12. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Executive Sponsor | _________________ | _________________ | ____/____/2026 |
| IT Head | _________________ | _________________ | ____/____/2026 |
| HR Director | _________________ | _________________ | ____/____/2026 |
| CISO | _________________ | _________________ | ____/____/2026 |
| Project Manager | _________________ | _________________ | ____/____/2026 |
