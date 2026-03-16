# Jonas Integration Plan: Connecting the UI to the Backend

**Project:** AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI / Frontend Lead)
**Date:** March 2026
**Purpose:** Planning document for integrating the React UI (Steps 1–6 complete) with the Python Orchestrator backend.

---

## Table of Contents

1. [What We Have vs What's Missing](#1-what-we-have-vs-whats-missing)
2. [The Big Picture: How Everything Connects](#2-the-big-picture-how-everything-connects)
3. [The Missing Piece: A Web API Layer](#3-the-missing-piece-a-web-api-layer)
4. [What the Orchestrator Actually Returns](#4-what-the-orchestrator-actually-returns)
5. [API Contract: Exact Endpoints to Build](#5-api-contract-exact-endpoints-to-build)
6. [Session Management: How Conversations Are Remembered](#6-session-management-how-conversations-are-remembered)
7. [Ticket Storage: How the Agent Dashboard Gets Its Data](#7-ticket-storage-how-the-agent-dashboard-gets-its-data)
8. [Integration Roadmap: Steps 7 to 10](#8-integration-roadmap-steps-7-to-10)
9. [Division of Work: Jonas vs Teammates](#9-division-of-work-jonas-vs-teammates)
10. [Cloud Deployment on Azure](#10-cloud-deployment-on-azure)
11. [Environment Variables Reference](#11-environment-variables-reference)
12. [Security Checklist](#12-security-checklist)

---

## 1. What We Have vs What's Missing

### Integration complete — all local components are done:

| Part | Status | Description |
|------|--------|-------------|
| React UI — Customer Chat Portal | ✅ Done | Real AI responses via `POST /api/chat`, session ID, loading spinner |
| React UI — Agent Dashboard | ✅ Done | Real tickets from API, resolve/reply/close actions wired |
| React UI — Admin Dashboard | ✅ Done | Real stat cards, pie chart, XAI traces from API |
| Python Orchestrator | ✅ Done (by teammates) | 7-agent pipeline, processes user messages |
| FastAPI Layer (`src/api.py`) | ✅ Done (Jonas) | 6 endpoints wrapping the Orchestrator, CORS, session + ticket storage |
| `ui/src/services/api.js` | ✅ Done (Jonas) | All 6 Axios call functions, base URL from env var |
| `requirements.txt` | ✅ Done | All Python dependencies listed for team + cloud |
| `ui/.env.development` | ✅ Done | `VITE_API_URL=http://localhost:8000` for local dev |
| Bug fixes (post-integration) | ✅ Done | Timezone UTC+8, action button persistence, custom reply display |

### Still pending:

| Part | Who | Description |
|------|-----|-------------|
| **Cloud deployment** | Both | Deploy backend to Azure, frontend to Vercel or Azure |
| **Daily interactions line chart** | Backend teammate | No time-series API endpoint yet — chart uses static mock data |
| **Agent routing table** | Backend teammate | No per-agent count endpoint yet — table uses static mock data |
| **Knowledge gap alerts** | Backend teammate | `detect_knowledge_gaps()` not yet exposed via API |

---

## 2. The Big Picture: How Everything Connects

Think of the system like a restaurant:
- The **customer** (browser) places an order at the **front counter** (React UI)
- The **counter** talks to the **kitchen manager** (FastAPI web server) via a **ticket slip** (HTTP request)
- The **kitchen manager** passes the order to the **head chef** (Orchestrator)
- The **head chef** routes work to the **specialist cooks** (7 agents: Triage, Security, RAG, etc.)
- The result travels back the same way — agents → Orchestrator → FastAPI → React UI → customer

```
┌─────────────────────────────────────────────────────────────────────┐
│  BROWSER (Customer / Agent / Admin)                                 │
│  React UI  ─── Axios HTTP calls ───►  FastAPI Web Server           │
│                                        (NEW — needs to be built)   │
│                                              │                      │
│                                              ▼                      │
│                                       Orchestrator                  │
│                                       (src/orchestrator.py)         │
│                                              │                      │
│                         ┌────────────────────┼─────────────────┐   │
│                         ▼                    ▼                  ▼   │
│                   TriageAgent       SecurityAgent         AnalyticsAgent  │
│                         │                    │                  │   │
│                    (route decision)     (block check)    (log stats) │
│                         │                                        │   │
│              ┌──────────┴──────────┐                            │   │
│              ▼                     ▼                            │   │
│     ResolutionAgent    InformationRetrievalAgent        EscalationAgent │
│              │                     │                            │   │
│              └──────────┬──────────┘                            │   │
│                         ▼                                        │   │
│                  VerificationAgent                               │   │
│                  (fact-checks response)                          │   │
└─────────────────────────────────────────────────────────────────────┘

CLOUD DEPLOYMENT:
  Frontend → Vercel or Azure Static Web Apps
  Backend  → Azure App Service or Azure Container Apps
```

**Key insight:** The Orchestrator already works perfectly. We are NOT changing it. We are just wrapping it with a web server so the browser can talk to it over HTTP (the standard language of the internet).

---

## 3. The Missing Piece: A Web API Layer

The current backend only runs as a command-line tool (`python src/main.py`). A browser cannot call a command-line tool — it can only make HTTP requests (the same way you open a website).

**The solution is FastAPI** — a Python library that turns the Orchestrator into a proper web server that the browser can communicate with.

Think of FastAPI as a "translator" that:
1. Listens for HTTP requests from the React UI
2. Calls the Orchestrator's `process_request()` function
3. Sends the result back as a JSON response

**Why FastAPI?**
- It is Python (same language as the backend — no new language to learn for teammates)
- It is fast and modern
- It automatically generates interactive documentation you can test in a browser
- It is widely used in professional AI/ML systems
- It works well on Azure

**The file to create:** `src/api.py` (or `src/app.py`)

This is a teammate task (see Section 9), but you should understand what it does.

---

## 4. What the Orchestrator Actually Returns

Before we design the API, it helps to understand exactly what data the Orchestrator produces. Here is what it returns when a customer sends a message (from reading `src/orchestrator.py`):

### When a message is RESOLVED normally:

```json
{
  "agent": "ResolutionAgent",
  "analysis": {
    "category": "billing",
    "priority": "low",
    "sentiment": "neutral",
    "confidence_score": 0.85,
    "risk_score": 0.0,
    "requires_human": false,
    "explanation": "Matched billing keyword 'bill' | Sentiment detected as neutral"
  },
  "response": {
    "status": "resolved",
    "message": "Your bill was last updated on...",
    "confidence": 0.82
  }
}
```

### When a message is ESCALATED to a human agent:

```json
{
  "agent": "EscalationAgent",
  "analysis": {
    "category": "billing",
    "priority": "high",
    "sentiment": "negative",
    "confidence_score": 0.85,
    "risk_score": 0.2,
    "requires_human": true,
    "explanation": "Urgent keyword detected | Sentiment detected as negative"
  },
  "response": {
    "status": "escalated",
    "queue": "billing_support",
    "message": "Your issue is being transferred to a support specialist."
  }
}
```

### When a message is BLOCKED by security:

```json
{
  "agent": "SecurityComplianceAgent",
  "response": {
    "status": "blocked",
    "message": "Request blocked due to security policy."
  }
}
```

### Possible values for key fields:

| Field | Possible Values |
|-------|----------------|
| `agent` | `"ResolutionAgent"`, `"InformationRetrievalAgent"`, `"EscalationAgent"`, `"SecurityComplianceAgent"` |
| `analysis.category` | `"billing"`, `"technical_support"`, `"account_issue"`, `"order_status"`, `"general_inquiry"`, `"security_alert"` |
| `analysis.priority` | `"low"`, `"high"` |
| `analysis.sentiment` | `"positive"`, `"neutral"`, `"negative"` |
| `response.status` | `"resolved"`, `"escalated"`, `"blocked"` |
| `response.queue` (when escalated) | `"billing_support"`, `"technical_support"`, `"general_support"`, `"security_compliance_team"`, `"security_verification_team"` |

### What the analytics endpoint returns (from `get_system_insights()`):

```json
{
  "total_requests": 42,
  "resolved_count": 38,
  "resolution_rate": "90.48%",
  "category_breakdown": {
    "billing": 12,
    "technical_support": 8,
    "general_inquiry": 15,
    "account_issue": 4,
    "order_status": 3
  },
  "hallucination_rate": 0.024,
  "escalation_rate": 0.095,
  "avg_retrieval_confidence": 0.74
}
```

---

## 5. API Contract: Exact Endpoints to Build

This is the formal "contract" between the UI (Jonas) and the API (teammates). Both sides must agree on this before building.

---

### Endpoint 1: Send a Chat Message

**What it does:** Customer types a message → Orchestrator processes it → reply comes back

```
POST /api/chat
```

**Request (what UI sends):**
```json
{
  "message": "I have a problem with my bill",
  "session_id": "session_abc123"
}
```

> `session_id` is a random ID the browser generates to track the conversation. It lets the server remember previous messages in the same chat. If omitted, a new session is created.

**Response (what UI receives):**
```json
{
  "session_id": "session_abc123",
  "agent": "ResolutionAgent",
  "status": "resolved",
  "message": "I understand you have a billing concern...",
  "analysis": {
    "category": "billing",
    "priority": "low",
    "sentiment": "neutral",
    "confidence_score": 0.85,
    "explanation": "Matched billing keyword 'bill'"
  }
}
```

Or, if escalated:
```json
{
  "session_id": "session_abc123",
  "agent": "EscalationAgent",
  "status": "escalated",
  "message": "Your issue is being transferred to a support specialist.",
  "ticket_id": "TKT-00042",
  "queue": "billing_support",
  "analysis": {
    "category": "billing",
    "priority": "high",
    "sentiment": "negative",
    "confidence_score": 0.85,
    "explanation": "Urgent keyword detected | Sentiment detected as negative"
  }
}
```

---

### Endpoint 2: Get All Escalated Tickets

**What it does:** Agent Dashboard loads the list of tickets awaiting human review

```
GET /api/tickets
```

**Response:**
```json
[
  {
    "ticket_id": "TKT-00042",
    "customer_session_id": "session_abc123",
    "status": "open",
    "queue": "billing_support",
    "category": "billing",
    "priority": "high",
    "sentiment": "negative",
    "created_at": "2026-03-16T09:30:00Z",
    "last_message": "I have been waiting 3 days for my refund!",
    "conversation_history": [
      { "role": "user", "content": "My bill is wrong" },
      { "role": "assistant", "content": "I understand..." },
      { "role": "user", "content": "I have been waiting 3 days for my refund!" }
    ]
  }
]
```

---

### Endpoint 3: Get a Single Ticket

**What it does:** Agent clicks a ticket to see its full detail and conversation history

```
GET /api/tickets/{ticket_id}
```

**Response:** Same structure as a single item from the list above.

---

### Endpoint 4: Resolve a Ticket

**What it does:** Human agent approves, sends a custom reply, or closes a ticket

```
POST /api/tickets/{ticket_id}/resolve
```

**Request:**
```json
{
  "action": "approved",
  "agent_reply": "We have processed your refund. It will arrive in 3-5 business days."
}
```

> `action` can be: `"approved"`, `"custom_reply"`, `"closed"`

**Response:**
```json
{
  "ticket_id": "TKT-00042",
  "status": "resolved",
  "resolved_by": "human_agent",
  "agent_reply": "We have processed your refund..."
}
```

---

### Endpoint 5: Get Analytics Summary

**What it does:** Admin Dashboard loads the main stat cards and charts

```
GET /api/analytics/summary
```

**Response:** Directly passes through `orchestrator.get_system_insights()`:
```json
{
  "total_requests": 157,
  "resolved_count": 144,
  "resolution_rate": "91.72%",
  "escalation_rate": 0.08,
  "hallucination_rate": 0.02,
  "avg_retrieval_confidence": 0.78,
  "category_breakdown": {
    "billing": 45,
    "technical_support": 38,
    "general_inquiry": 52,
    "account_issue": 14,
    "order_status": 8
  }
}
```

---

### Endpoint 6: Get XAI Decision Traces

**What it does:** Admin Dashboard shows the AI's decision reasoning for recent interactions

```
GET /api/analytics/xai-traces
```

**Response:**
```json
[
  {
    "ticket_id": "TKT-00041",
    "agent_path": "Triage → Resolution",
    "category": "billing",
    "priority": "low",
    "decision_reason": "Matched billing keyword 'bill' | Sentiment detected as neutral",
    "confidence": 0.85,
    "timestamp": "2026-03-16T09:28:00Z"
  }
]
```

> This is built from the `analytics_db` stored in the Orchestrator — each logged interaction has `analysis.explanation` which is the XAI trace.

---

## 6. Session Management: How Conversations Are Remembered

**The problem:** The Orchestrator's `process_request(user_input, history)` function requires you to pass in the full conversation history each time. But a web server receives thousands of separate HTTP requests. How does it know which past messages belong to which customer?

**The solution:** Session IDs.

When a customer first opens the chat:
1. The UI generates a random session ID (e.g., `"session_abc123"`)
2. The UI stores this ID in the browser's memory
3. Every `POST /api/chat` request includes this session ID
4. The FastAPI server keeps a dictionary like `sessions = { "session_abc123": [...history...] }`
5. When a new message arrives, the server looks up the history, passes it to the Orchestrator, then saves the updated history back

```
Customer Browser                 FastAPI Server               Orchestrator
     │                                │                            │
     │── POST /api/chat ─────────────►│                            │
     │   { message, session_id }      │                            │
     │                                │  history = sessions[id]    │
     │                                │── process_request(msg, history) ──►│
     │                                │◄─────────── result ────────────────│
     │                                │  sessions[id] = updated_history    │
     │◄─── { response } ─────────────│                            │
```

**Note for Jonas:** This is handled entirely on the backend (FastAPI + teammates). You don't need to build this. You just need to make sure the UI:
1. Generates and stores a `session_id` when the chat loads
2. Sends that `session_id` with every message

---

## 7. Ticket Storage: How the Agent Dashboard Gets Its Data

**The problem:** When the Orchestrator escalates a ticket, it currently just returns a JSON response and forgets about it. There is no persistent list of "open tickets" anywhere.

**The solution:** The FastAPI layer maintains an in-memory ticket store (a simple Python list or dictionary). When an escalation happens:
1. `POST /api/chat` receives an escalation response from the Orchestrator
2. FastAPI generates a `ticket_id` (e.g., `"TKT-00042"`)
3. FastAPI saves the ticket to the ticket store
4. `GET /api/tickets` reads from this store

**Simple implementation (teammates build this):**
```python
# In api.py
tickets_store = {}   # { "TKT-00042": { ...ticket data... } }
ticket_counter = 0

# When escalation happens:
ticket_counter += 1
ticket_id = f"TKT-{ticket_counter:05d}"
tickets_store[ticket_id] = { ...ticket data... }
```

**Important limitation:** Because this is in-memory (RAM), tickets are lost every time the server restarts. For a production system, this would move to a database (PostgreSQL, Azure Cosmos DB, etc.). For this prototype, in-memory is acceptable.

---

## 8. Integration Roadmap: Steps 7 to 10

These steps replace the mock data with real backend connections.

---

### Step 7A: Teammates Build the FastAPI Layer

**Goal:** Create `src/api.py` that wraps the Orchestrator as a web server.

**Who does this:** Backend teammate (Python developer)

**What to build:**
- Install FastAPI: `pip install fastapi uvicorn`
- Create `src/api.py` with the 6 endpoints from Section 5
- Add CORS middleware so the browser can connect
- Add session management (in-memory dictionary)
- Add ticket store (in-memory dictionary)
- Test it works locally with the interactive docs at `http://localhost:8000/docs`

**Deliverable:** Running `uvicorn src.api:app --reload` starts the server. All 6 endpoints return real data.

**Jonas's action during this step:** Share this plan document's Section 5 (API Contract) with the teammate. Ask them to follow that exact contract so your UI can connect without surprises.

---

### Step 7B: Jonas Wires Up the UI

**Goal:** Replace all mock data in the UI with real Axios calls to the FastAPI backend.

**Who does this:** Jonas

**What to build:**
1. Create `ui/src/services/api.js` — all Axios HTTP calls in one place
2. Update `CustomerChat.jsx` — replace mock responses with `POST /api/chat`
3. Update `AgentDashboard.jsx` — replace mock tickets with `GET /api/tickets` and `POST /api/tickets/{id}/resolve`
4. Update `AdminDashboard.jsx` — replace mock stats with `GET /api/analytics/summary` and `GET /api/analytics/xai-traces`
5. Add loading spinners while data is fetching
6. Add error messages if the backend is unreachable

**Prerequisite:** Step 7A must be complete and the FastAPI server must be running locally first.

**Deliverable:** UI files updated. End-to-end test: type a message in chat → real AI response appears.

**Detailed sub-steps for Jonas (expand each when ready to execute):**

| Sub-step | File | What to do |
|----------|------|-----------|
| 7B-1 | `ui/src/services/api.js` | Create file with all Axios call functions |
| 7B-2 | `ui/.env.development` | Add `VITE_API_URL=http://localhost:8000` |
| 7B-3 | `ui/src/pages/CustomerChat.jsx` | Wire up real chat API |
| 7B-4 | `ui/src/pages/AgentDashboard.jsx` | Wire up real ticket API |
| 7B-5 | `ui/src/pages/AdminDashboard.jsx` | Wire up real analytics API |

---

### Step 8: Styling Polish and Error States

**Goal:** Make the UI look production-ready and handle failure gracefully.

**Who does this:** Jonas

**What to polish:**
- Loading spinners (Ant Design `Spin` component) on all data-fetching sections
- Empty state messages ("No tickets yet" when queue is empty)
- Error banners if API calls fail
- Disable chat input while waiting for AI response (so customer cannot double-send)
- Mobile-responsive layout check (test on phone screen size)
- Consistent colour scheme across all 3 pages

**Deliverable:** UI looks polished. All edge cases handled.

---

### Step 9: End-to-End Testing

**Goal:** Verify the complete system works — real customer message flows all the way through to analytics dashboard.

**Who does this:** Jonas + teammates together

**Test scenarios to check:**

| Test Case | Expected Result |
|-----------|----------------|
| Customer types a billing question | AI responds with resolution, category = "billing" shown |
| Customer types an urgent frustrated message | Escalated to human, ticket appears in Agent Dashboard |
| Customer types a jailbreak attempt | Blocked response shown, no ticket created |
| Agent approves AI response | Ticket status changes to "Resolved" |
| Agent sends custom reply | Custom reply stored, ticket resolved |
| Admin Dashboard loads | Real stats from analytics agent appear |
| Backend is turned off | UI shows friendly error message, does not crash |

**Deliverable:** All test cases pass. Screenshots taken for report.

---

### Step 10: Cloud Deployment

**Goal:** Deploy the fully integrated system to the cloud so anyone can access it via a URL.

**Who does this:** Both Jonas and teammates coordinate

**Architecture:**
```
Internet Users
      │
      ▼
┌─────────────────────────────────────────┐
│  FRONTEND                               │
│  Vercel (free) or Azure Static Web Apps │
│  URL: https://ai-support.vercel.app     │
└─────────────────────────────────────────┘
      │ HTTPS API calls
      ▼
┌─────────────────────────────────────────┐
│  BACKEND                                │
│  Azure App Service (Python)             │
│  URL: https://ai-support-api.azurewebsites.net │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  OpenAI API (external)                  │
│  Called by ConversationAgent +          │
│  VerificationAgent                      │
└─────────────────────────────────────────┘
```

**Backend deployment steps (teammate does this):**
1. Create Azure account (free trial available)
2. Create Azure App Service (Python 3.11, Linux)
3. Set environment variable `OPENAI_API_KEY` in Azure App Service settings (NEVER in code)
4. Deploy with: `az webapp up --name ai-support-api --runtime "PYTHON:3.11"`
5. Note the backend URL (e.g., `https://ai-support-api.azurewebsites.net`)

**Frontend deployment steps (Jonas does this):**
1. Create Vercel account (free) at vercel.com
2. Connect your GitHub repository to Vercel
3. Set root directory to `ui/`
4. Set environment variable in Vercel dashboard: `VITE_API_URL=https://ai-support-api.azurewebsites.net`
5. Deploy — Vercel auto-deploys on every `git push`

**Deliverable:** Live URL that anyone on the team can open in their browser. Full demo ready.

---

## 9. Division of Work: Jonas vs Teammates

| Task | Jonas | Teammates | Notes |
|------|-------|-----------|-------|
| Share API contract (Section 5) with teammates | Do | — | Do this first |
| Build FastAPI `src/api.py` | — | Do | Prerequisites: FastAPI, uvicorn installed |
| Session management in FastAPI | — | Do | In-memory sessions dictionary |
| Ticket storage in FastAPI | — | Do | In-memory tickets dictionary |
| CORS configuration in FastAPI | — | Do | Allow localhost:5173 and production URL |
| Create `ui/src/services/api.js` | Do | — | After FastAPI is ready |
| Wire up Customer Chat to real API | Do | — | After 7A done |
| Wire up Agent Dashboard to real API | Do | — | After 7A done |
| Wire up Admin Dashboard to real API | Do | — | After 7A done |
| Loading states and error handling in UI | Do | — | Step 8 |
| End-to-end testing | Both | Both | Step 9 |
| Deploy backend to Azure App Service | — | Do | Step 10 |
| Deploy frontend to Vercel | Do | — | Step 10 |
| Set environment variables on Vercel | Do | — | Step 10 |
| Set environment variables on Azure | — | Do | Step 10 |

**The key coordination moment:** Before Jonas starts Step 7B, the teammate must confirm:
1. FastAPI server is running locally at `http://localhost:8000`
2. The interactive API docs at `http://localhost:8000/docs` work
3. `POST /api/chat` returns a real response from the Orchestrator

---

## 10. Cloud Deployment on Azure

### Option A: Recommended for this project (simplest)

| Component | Service | Cost | Notes |
|-----------|---------|------|-------|
| Backend API | Azure App Service (Free tier or B1) | Free / ~$13/month | Python web app |
| Frontend | Vercel | Free | Auto-deploys from GitHub |
| OpenAI calls | OpenAI API | Pay per use | Keep usage low for prototype |

### Option B: All on Azure (if required by course)

| Component | Service | Cost | Notes |
|-----------|---------|------|-------|
| Backend API | Azure App Service | ~$13/month | Python web app |
| Frontend | Azure Static Web Apps | Free tier available | React frontend |
| OpenAI calls | OpenAI API | Pay per use | |

### Option C: Containerised (more advanced, better for production)

| Component | Service | Notes |
|-----------|---------|-------|
| Backend API | Azure Container Apps | Package everything in Docker |
| Frontend | Azure Static Web Apps | |

**Recommendation for this course:** Use Option A. It is the fastest to set up and avoids spending money during prototype phase.

---

## 11. Environment Variables Reference

Environment variables are settings that are stored outside the code — think of them as "secret switches" that you set on the server, not in the code file. This prevents secrets like API keys from being accidentally shared.

### Backend (FastAPI server):

| Variable | Value | Where to set |
|----------|-------|-------------|
| `OPENAI_API_KEY` | Your OpenAI key | Azure App Service → Configuration → App Settings |

### Frontend (React / Vite):

| Variable | Value in Development | Value in Production |
|----------|---------------------|---------------------|
| `VITE_API_URL` | `http://localhost:8000` | `https://ai-support-api.azurewebsites.net` |

**How to set for local development:**
1. Create a file called `ui/.env.development` (not committed to Git)
2. Add: `VITE_API_URL=http://localhost:8000`
3. In code, access as: `import.meta.env.VITE_API_URL`

**How to set for Vercel production:**
- Vercel Dashboard → Your project → Settings → Environment Variables → Add

---

## 12. Security Checklist

Before the final demo and submission, verify all of these:

- [ ] `.env` file is listed in the root `.gitignore` (it currently is NOT — fix this immediately)
- [ ] `.env.development` file is listed in `ui/.gitignore`
- [ ] OpenAI API key is NOT hardcoded anywhere in Python or JavaScript files
- [ ] OpenAI API key is set via environment variable only (Azure App Settings or local `.env`)
- [ ] If the current API key was ever committed to GitHub, revoke it and generate a new one
- [ ] CORS is configured to only allow your specific frontend URL in production (not all origins)
- [ ] The backend validates user input length (prevent extremely long messages)
- [ ] The backend has a rate limit (prevent spamming the OpenAI API with cost)

---

## Summary: Integration Status

**Local integration is complete.** All three dashboards are connected to the real Orchestrator backend. The system can be run locally by any team member — see `QUICKSTART.md` for the step-by-step setup guide.

**Remaining work before final submission:**

1. **Cloud deployment** — Deploy backend to Azure App Service, frontend to Vercel. Set environment variables on both platforms (`OPENAI_API_KEY` on Azure, `VITE_API_URL` on Vercel).

2. **Security checklist** — Verify `.env` and `.env.development` are git-ignored and API key is not hardcoded anywhere. See Section 12.

3. **Static mock sections** (optional enhancements) — The daily interactions line chart, agent routing table, and knowledge gap alerts still use hardcoded data. These require additional backend endpoints if real data is needed for the submission.

---

*This document will be updated as integration progresses. Last updated: March 2026.*
