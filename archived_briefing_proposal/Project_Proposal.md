### Project Proposal: AI-Powered Customer Support Triage and Resolution System (Enhanced)

**1. Project Title:**
AI-Powered Customer Support Triage and Resolution System (Enhanced)

**2. Project Sponsor:**
(To be determined - for the purpose of this project, we can assume a fictional sponsor, e.g., "Head of Customer Experience, Acme Corporation")

**3. Project Members:**
a) Ting Ching Jong
b) Toh Chan Hao
c) Teng Ching Yee
d) Tang You Wei
e) Ooi Yu Jie


**4. Overview:**
This project aims to develop a sophisticated multi-agent AI system that automates and secures the end-to-end customer support lifecycle. The system utilizes advanced agentic patterns (LangGraph) to manage complex, multi-turn interactions. Beyond simple automation, this system prioritizes trust through integrated Explainable AI (XAI), robust Cybersecurity guards, and a professional LLMOps pipeline for continuous evaluation and safety.

**5. General Architecture:**
The system follows a modular, agentic architecture managed by a state-oriented Orchestrator. 
*   **Orchestration Logic:** Uses LangGraph to manage state across agents, allowing for loops, retries, and human-in-the-loop (HITL) interventions.
*   **Storage:** Vector Database (ChromaDB/Pinecone) for RAG and a Graph Database/Session Store for conversation state.
*   **Security Layer:** Integrated Guardrails (LlamaGuard) for real-time monitoring.

The agents in the system are:

*   **Triage Agent:** Analyzes intent, sentiment, and urgency using few-shot prompting.
*   **Security & Compliance Agent (New):** Masks PII (Personally Identifiable Information) and filters for jailbreak attempts/malicious prompts.
*   **Information Retrieval (RAG) Agent:** Performs semantic search across the knowledge base with sophisticated re-ranking.
*   **Verification Agent (New):** A "Critic" agent that checks IR/Resolution outputs for hallucinations and factual consistency.
*   **Resolution Agent:** Executes workflows (APIs/scripts) for common tasks like password resets or order tracking.
*   **Escalation Agent:** Synthesizes context for human agents when AI confidence is low or sentiment is critical.
*   **Analytics & Feedback Agent:** Periodically analyzes logs to identify "knowledge gaps" and drift.

**6. Scope of Work:**
The expanded scope focuses on "Enterprise-Grade AI" practices:

*   **Responsible AI (XAI):** Implementing a multi-layered XAI strategy including Decision Traceability (chain-of-thought logs) and feature attribution for the Triage Agent.
*   **Advanced Cybersecurity:** Implementing "Defense in Depth" with input sanitization, output filtering, and a dedicated Security Risk Register for AI-specific threats (Prompt Injection, Insecure Output Handling).
*   **Agentic AI & Orchestration:** Implementing complex state-management using LangGraph, ensuring agent autonomy within defined boundaries.
*   **LLMOps Pipeline:** Developing a full pipeline for automated RAG evaluation (RAGAS), synthetic test data generation, and CI/CD for prompt versioning.
*   **UI Prototype:** A comprehensive dashboard for (1) Customers, (2) Support Agents (HITL), and (3) AI Admins (Analytics/XAI).

**7. Effort Estimates (Work Breakdown Structure):**

| Phase | Task | Total Hours |
| :--- | :--- | :--- |
| **Phase 1: Research & Design** | Literature review on XAI/Security, detailed architecture (LangGraph state), and prompt engineering strategy. | **100** |
| **Phase 2: Core Development** | Developing the 7 agents, Orchestrator logic, and integration with Vector DB/APIs. | **220** |
| **Phase 3A: MLOps / LLMOps** | Establishing automated RAG evaluation using RAGAS, generating and maintaining synthetic datasets for regression testing, managing prompt versioning, and continuously monitoring model performance and quality. | **65** |
| **Phase 3B: Infra** | CI/CD setup, secure vector database provisioning, centralized logging and telemetry, monitoring dashboards for observability, and environment separation across development, testing, and production. | **35** |
| **Phase 4: Responsible AI & Security** | Implementing bias detection, XAI reporting, PII masking, and performing a security audit. | **80** |
| **Phase 5: Testing & UI** | Integration testing, synthetic data generation, and building the 3-tier UI Prototype. | **50** |
| **Phase 6: Final Docs & Wrap-up** | Technical Report, Individual Agent Reports, and Presentation preparation. | **50** |
| **Total Estimated Effort** | | **600** |

This equates to **120 hours (15 man days)** of effort per member for our team of 5.
