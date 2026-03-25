# Project Development Log: AI-Powered Customer Support System

**Date:** 5 January 2026  
**Status:** Prototype Phase Completed

## 1. Initial Objectives
The goal was to design and implement a multi-agent system based on the NUS ISS "Architecting AI Systems" project briefing. Key requirements included:
- Demonstrate **Agentic AI** design patterns.
- Incorporate **Explainable AI (XAI)**.
- Address **AI Cybersecurity** (specifically prompt injection).
- Implement **MLOps/LLMOps** principles (CI/CD, testing, logging).

## 2. Implemented Architecture
We built a microservices-inspired architecture using a central `Orchestrator` and specialized agents:

- **Triage Agent:** Performed intent classification, priority assignment, and security validation. Provided natural language explanations for its logic.
- **Information Retrieval Agent:** Simulated RAG (Retrieval-Augmented Generation) using a keyword-searchable knowledge base.
- **Resolution Agent:** Handled automated workflows (Password Reset, Refund Processing, Order Status).
- **Escalation Agent:** Managed hand-off to human agents via simulated ticket creation.
- **Analytics Agent:** Tracked system performance, resolution rates, and category breakdowns.

## 3. Key Milestones & Decisions
- **Project Scaffolding:** Initialized directory structure (`src`, `tests`, `docs`, `ui`) and Git repository.
- **Keyword-Triggered XAI:** Decided to implement explainability by tracking and reporting the specific keywords that triggered classification.
- **Multi-Layered Security:** Integrated a pre-processing validation step in the Triage Agent to block prompt injection before it reaches the "logic" layer.
- **Iterative Testing:** Created a suite of unit tests for every agent to ensure reliability and facilitate future refactoring.
- **CLI Development:** Built an interactive command-line interface to demonstrate end-to-end user flows.

## 4. Final Project State
- **Source Code:** Located in `src/`.
- **Tests:** Located in `tests/`. Run via `python tests/test_*.py`.
- **Documentation:**
    - `README.md`: High-level overview.
    - `docs/Explainable_AI.md`: Details on transparency.
    - `docs/Cybersecurity_Report.md`: Details on threat mitigation.
    - `Project_Proposal.md`: The original concept document.

## 5. How to Continue
To resume development in a future session:
1.  Run the CLI: `python src/cli.py`.
2.  Add more complex NLP models (e.g., using HuggingFace or OpenAI API) to replace the keyword matching in `triage_agent.py`.
3.  Connect a real database (like PostgreSQL or MongoDB) to the `AnalyticsAgent`.
4.  Implement a real Vector Database (like FAISS or ChromaDB) in the `InformationRetrievalAgent`.

---

# Phase 2 — Full-Stack Integration & Enhancement

**Date:** March 2026
**Status:** Complete

## 6. What Was Built in Phase 2

The system was substantially expanded from the CLI prototype into a production-like full-stack application. Key additions:

### 6.1 React UI (3 Dashboards)
Built with React + Vite + Ant Design:
- **Customer Chat Portal** — real-time chat with the AI; shows agent name, priority tag, sentiment tag, and ticket reference on escalation
- **Support Agent Dashboard** — human agents review the escalated ticket queue, read conversation history, approve the AI-drafted reply or write a custom one, or close the ticket
- **AI Admin Dashboard** — analytics stat cards, daily interactions chart, agent routing breakdown, knowledge gap alerts, and an XAI decision traces table

### 6.2 FastAPI Backend (`src/api.py`)
A REST API layer connecting the React UI to the Orchestrator:
- `POST /api/chat` — customer message → Orchestrator → response + optional ticket creation
- `GET/POST /api/tickets` — ticket queue and resolution
- `GET /api/analytics/summary` — system-wide stats + daily interactions + agent routing + knowledge gaps
- `GET /api/analytics/xai-traces` — per-request AI decision trace log

### 6.3 ChromaDB Vector Database (`src/vector_db.py`)
Replaced simulated keyword retrieval with real semantic search:
- `customer_support_kb` collection seeded with 15 curated knowledge base documents
- `approved_answers` collection grows automatically as agents approve/custom-reply tickets (self-learning)
- `search()` queries both collections and merges results by similarity score

### 6.4 Explainable AI (XAI) — Step T
The Triage Agent generates a structured natural-language explanation for every routing decision, including: detected category and how (keyword vs. ML model), confidence percentage, sentiment, priority, and full routing rationale (e.g. "Routed to: Human Agent — negative sentiment, high priority"). This is logged and surfaced in the Admin Dashboard XAI traces table.

### 6.5 Human-in-the-Loop (HITL) — Genuine Implementation
When escalating, the system immediately generates an LLM-drafted suggested response for the human agent to review. The agent can approve it (AI was right), write their own reply (AI was wrong), or close without reply. Both outcomes are stored as validated Q&A pairs in the vector DB so the AI can learn from human corrections.

### 6.6 Security — API Key Authentication
All agent-facing and admin-facing endpoints are protected by a shared `INTERNAL_API_KEY` validated via the `X-API-Key` header. The customer chat endpoint remains unauthenticated (public-facing). Keys are loaded from environment variables; never committed to git.

## 7. Current Project State (March 2026)

- **Backend:** `src/api.py` (FastAPI), `src/orchestrator.py`, `src/agents/`, `src/vector_db.py`
- **Frontend:** `ui/src/` — three dashboards, shared utilities in `ui/src/utils/formatters.js`
- **Docs:** `QUICKSTART.md` (local setup), `DEPLOYMENT.md` (cloud deployment), `Jonas_Design_Decisions.md` (UI behaviour rationale)
- **Tests:** `tests/` — unit tests for all agents
