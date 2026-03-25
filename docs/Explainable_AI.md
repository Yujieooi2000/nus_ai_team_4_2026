# Explainable AI (XAI) and Responsible AI Framework

## 1. Overview
In alignment with the expanded scope of the AI-Powered Customer Support System, this document outlines our strategy for ensuring the system is transparent, fair, and accountable. Our goal is to move beyond "black-box" models to a system where every agent decision is traceable and justifiable.

## 2. Agent-Specific XAI Strategies

### 2.1 Triage Agent: Intent Attribution
- **Technique:** Structured natural-language reasoning trace generated per request.
- **Implementation:** For every customer message, the Triage Agent produces an `explanation` field that states: the detected category and how it was determined (keyword match vs. ML model), confidence percentage, detected sentiment, assigned priority, and the routing decision with specific reasons (e.g. *"Routed to: Human Agent — negative sentiment, high priority"*). This explanation is stored in the analytics log and surfaced in the Admin Dashboard XAI traces table.
- **Goal:** Allow human supervisors to audit exactly why a query was routed to a specific agent or escalated.

### 2.2 Information Retrieval (RAG) Agent: Evidence-Based Answers
- **Technique:** Semantic vector search with source attribution.
- **Implementation:** ChromaDB is used for semantic similarity search over a curated knowledge base (`customer_support_kb`). A second collection (`approved_answers`) accumulates human-validated Q&A pairs over time as agents approve or correct AI replies. The retrieval agent merges results from both collections by similarity score before generating a response.
- **Goal:** Ground responses in verified knowledge; prevent hallucinations by limiting the LLM to retrieved context.

### 2.3 Verification Agent (The Critic)
- **Role:** Acts as an internal auditor between the IR Agent and the Resolution Agent. Evaluates faithfulness and answer relevance.
- **Goal:** Provide a score-based justification for why a response was deemed safe or unsafe to send to the customer. Responses that fail verification are flagged for escalation rather than being sent directly.

## 3. Responsible AI Practices

### 3.1 Bias Mitigation
- **Strategy:** Regular audits of the training/few-shot data to ensure no demographic bias in sentiment analysis or triage logic.
- **Metric:** Disparate impact analysis on triage accuracy across different customer segments.

### 3.2 Human-in-the-Loop (HITL)
- **Implementation:** For queries with low confidence scores or high negative sentiment, the system automatically escalates to a human agent. When escalating, the system generates an LLM-drafted suggested response for the agent to review — the agent can approve it, write a custom reply, or close the ticket without reply.
- **Self-learning:** Both approved AI responses and human corrections are stored back into the vector database (`approved_answers` collection), so the system improves over time from human oversight.

## 4. XAI Traces — Admin Dashboard
Every processed request is recorded in the analytics log with the following XAI fields:

| Field | Description |
|---|---|
| `trace_id` | Sequential identifier (TRACE-0001, TRACE-0002, …) |
| `agent_path` | Which agents handled the request (e.g. "Triage → IR → Verification → Resolution") |
| `category` | Detected intent category |
| `priority` | Assigned priority (High / Medium / Low) |
| `sentiment` | Detected customer sentiment |
| `confidence` | Triage confidence score (0–1) |
| `decision_reason` | Full natural-language explanation from the Triage Agent |
| `status` | Final outcome (resolved / escalated / blocked) |
| `timestamp` | UTC timestamp of the request |

These traces are served by `GET /api/analytics/xai-traces` and displayed in a searchable table in the Admin Dashboard.

## 5. Documentation & Traceability
All agent interactions, internal reasoning traces, and verification scores are logged in a structured format to support the final project audit and ensure complete accountability.