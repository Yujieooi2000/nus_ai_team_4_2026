# AI-Powered Customer Support Triage and Resolution System (Enhanced)

This project implements a state-of-the-art multi-agent AI system designed to automate, secure, and explain customer support interactions. It is built to meet the rigorous requirements of the NUS-ISS Graduate Certificate in Architecting AI Systems.

## 🚀 Key Features (Expanded Scope)
- **Advanced Agentic Orchestration:** Utilizing **LangGraph** for complex, multi-turn state management and reasoning.
- **7-Agent Architecture:**
  - **Triage Agent:** Intent and sentiment analysis.
  - **Security & Compliance Agent:** PII masking and prompt injection protection.
  - **Information Retrieval (RAG) Agent:** Evidence-based knowledge retrieval.
  - **Verification Agent:** Hallucination detection and consistency checks.
  - **Resolution Agent:** Automated task execution.
  - **Escalation Agent:** Human-in-the-loop (HITL) context synthesis.
  - **Analytics Agent:** Trend discovery and drift monitoring.
- **Responsible AI (XAI):** Built-in reasoning traces and source attribution for every decision.
- **Cybersecurity:** Dedicated "Security Gatekeeper" agent and AI-specific risk management.
- **Enterprise LLMOps:** Automated RAG evaluation (RAGAS) and CI/CD for prompt engineering.

## 📊 Effort Commitment
- **Total Effort:** 600 Person-Hours (Approx. 15 days per team member).
- **Team Size:** 5 Members.

## 📂 Project Structure
- `src/agents/`: Individual agent logic and implementations.
- `src/orchestrator.py`: LangGraph-based state management.
- `docs/`: Detailed reports on XAI, Cybersecurity, and Project Progress.
- `tests/`: Unit, integration, and security red-teaming tests.
- `ui/`: Customer, Agent, and Admin dashboards.

## Getting Started

See **[QUICKSTART.md](QUICKSTART.md)** for step-by-step local setup instructions (Python environment, vector DB initialisation, backend, frontend).

For cloud deployment, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.