# Jonas API Plan: Building the Web API Layer

**Project:** AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI / Frontend Lead, also building the API Layer)
**Date:** March 2026
**Purpose:** Step-by-step guide for building `src/api.py` — the FastAPI web server that connects the React UI to the Python Orchestrator.

---

## Table of Contents

1. [What We Are Building and Why](#1-what-we-are-building-and-why)
2. [How the Code Will Be Structured](#2-how-the-code-will-be-structured)
3. [Prerequisites: What to Install](#3-prerequisites-what-to-install)
4. [The Step-by-Step Roadmap](#4-the-step-by-step-roadmap)
5. [Detailed Step Guides](#5-detailed-step-guides)
6. [How to Run and Test Locally](#6-how-to-run-and-test-locally)
7. [What Changes in the UI After This](#7-what-changes-in-the-ui-after-this)
8. [Progress Tracker](#8-progress-tracker)

---

## 1. What We Are Building and Why

### The analogy: A restaurant order window

Imagine the Orchestrator is a kitchen that can cook any dish perfectly. But right now, the kitchen has no order window — you can only walk into the kitchen yourself (CLI) to place an order. The React UI (the customer) is standing outside and cannot get in.

**FastAPI is the order window.** It:
- Listens for orders (HTTP requests) coming from the browser
- Passes the order to the kitchen (Orchestrator)
- Hands back the result (HTTP response)

### What currently exists vs what we are adding

```
BEFORE:                             AFTER:

Browser (React UI)                  Browser (React UI)
        |                                   |
        X  (no connection)          POST /api/chat  ← NEW
        |                                   |
CLI: python src/main.py       ►   FastAPI: src/api.py   ← NEW
        |                                   |
   Orchestrator                       Orchestrator
        |                                   |
    7 Agents                           7 Agents
```

### The file we are creating

**`src/api.py`** — A single Python file that:
1. Starts a web server on port 8000
2. Receives HTTP requests from the React UI
3. Calls `orchestrator.process_request()` with the message
4. Returns the result as JSON
5. Manages conversation history (so the AI remembers previous messages)
6. Stores escalated tickets (so the Agent Dashboard can list them)

---

## 2. How the Code Will Be Structured

Here is a visual map of `src/api.py` before we write any code:

```
src/api.py
│
├── SECTION 1: Imports
│   └── FastAPI, CORS, Pydantic, uuid, datetime, os, Orchestrator
│
├── SECTION 2: App Setup
│   ├── Create FastAPI app
│   ├── Add CORS (allow browser to connect)
│   └── Create Orchestrator instance (loads OpenAI key from .env)
│
├── SECTION 3: In-Memory Storage
│   ├── sessions = {}   ← stores conversation history per customer
│   └── tickets  = {}   ← stores escalated tickets for Agent Dashboard
│
├── SECTION 4: Request / Response Models
│   ├── ChatRequest   (message + session_id)
│   └── ResolveRequest (action + agent_reply)
│
└── SECTION 5: API Endpoints
    ├── POST /api/chat                     ← Customer sends a message
    ├── GET  /api/tickets                  ← Agent loads ticket list
    ├── GET  /api/tickets/{ticket_id}      ← Agent opens one ticket
    ├── POST /api/tickets/{ticket_id}/resolve ← Agent resolves a ticket
    ├── GET  /api/analytics/summary        ← Admin loads stats
    └── GET  /api/analytics/xai-traces     ← Admin loads AI decision log
```

---

## 3. Prerequisites: What to Install

Before writing code, the correct Python libraries must be installed.

**What needs to be installed (Python):**

| Library | What it does | Already installed? |
|---------|-------------|-------------------|
| `fastapi` | The web framework that creates the API server | No — need to install |
| `uvicorn` | The server "engine" that runs FastAPI | No — need to install |
| `python-dotenv` | Reads the `.env` file for the OpenAI key | Likely yes (used in `main.py`) |
| `textblob` | Sentiment analysis (used by Triage Agent) | Likely yes (used in agents) |
| `openai` | OpenAI API calls (used by ConversationAgent + VerificationAgent) | Likely yes |

**The install command (teammates or Jonas runs this once in terminal):**

```bash
pip install fastapi uvicorn
```

**After installing, create a `requirements.txt` file** so anyone who clones the repo knows what to install:

```
fastapi
uvicorn
python-dotenv
openai
textblob
```

This file lives at the project root (`requirements.txt`).

> **What is `requirements.txt`?** It is like a shopping list for Python. Anyone who downloads your code runs `pip install -r requirements.txt` and gets all the right libraries automatically. Cloud platforms like Azure also use this file to set up the server.

---

## 4. The Step-by-Step Roadmap

| Step | Name | Goal | Who |
|------|------|------|-----|
| A | Install dependencies | FastAPI and uvicorn available | Jonas |
| B | Create `requirements.txt` | Dependency list for team + cloud | Jonas |
| C | Create `src/api.py` — skeleton | Empty FastAPI app that starts up | Jonas |
| D | Add CORS + Orchestrator | Browser can connect, Orchestrator ready | Jonas |
| E | Add in-memory storage | Session and ticket stores set up | Jonas |
| F | Build `POST /api/chat` | Customer chat works end-to-end | Jonas |
| G | Build `GET /api/tickets` and `GET /api/tickets/{id}` | Agent Dashboard ticket list loads | Jonas |
| H | Build `POST /api/tickets/{ticket_id}/resolve` | Agent can resolve a ticket | Jonas |
| I | Build `GET /api/analytics/summary` | Admin Dashboard stats load | Jonas |
| J | Build `GET /api/analytics/xai-traces` | Admin Dashboard AI trace table loads | Jonas |
| K | Test all endpoints using `/docs` | All 6 endpoints verified working | Jonas |
| L | Wire up React UI (Step 7B from Integration Plan) | Mock data replaced with real API calls | Jonas |

**Estimated effort:** Steps A–K are all backend (`src/api.py`). Step L is frontend (UI files).

---

## 5. Detailed Step Guides

> **Note:** This section describes what each step involves conceptually. Actual code will be written and explained when we execute each step together. Do not start coding yet — review and approve this plan first.

---

### Step A: Install Dependencies

**Goal:** Make sure FastAPI and uvicorn are available.

**What to do:**
- Open a terminal in VS Code (Terminal → New Terminal)
- Make sure you are in the project root folder (not inside `ui/`)
- Run: `pip install fastapi uvicorn`

**How to verify it worked:**
- The terminal should show "Successfully installed fastapi..." with no errors

---

### Step B: Create `requirements.txt`

**Goal:** Record all Python dependencies so teammates and Azure know what to install.

**What to do:**
- Create a new file called `requirements.txt` at the project root
- List all required libraries (one per line)

**Deliverable:** `requirements.txt` exists at project root.

---

### Step C: Create `src/api.py` — Skeleton

**Goal:** Create the API file with just enough to start the server and confirm it runs.

**What to do:**
- Create `src/api.py`
- Import FastAPI, create the app instance
- Add one simple "health check" endpoint: `GET /` → returns `{"status": "ok"}`

**How to verify it worked:**
- Run: `python -m uvicorn src.api:app --reload --port 8000`
- Open browser at `http://localhost:8000/` — should see `{"status": "ok"}`
- Open browser at `http://localhost:8000/docs` — should see the interactive API documentation

> **What is `/docs`?** FastAPI automatically generates an interactive web page where you can test every endpoint by clicking a button. No extra tools needed. This is very useful for testing before the UI is connected.

---

### Step D: Add CORS and Orchestrator

**Goal:** Allow the browser to connect (CORS), and load the Orchestrator so it is ready to process requests.

**What is CORS?**

CORS stands for Cross-Origin Resource Sharing. Browsers have a built-in security rule that blocks JavaScript code from calling a server on a different "origin" (domain + port). Your React app runs on `localhost:5173` and the API runs on `localhost:8000` — different ports = different origins = blocked by default.

Adding CORS middleware to FastAPI tells the browser: "Yes, requests from `localhost:5173` are allowed."

**What to do:**
- Import and add `CORSMiddleware` to the FastAPI app
- Specify allowed origins: `http://localhost:5173` (development) + your future Vercel URL (production)
- Load the Orchestrator: `orchestrator = Orchestrator(api_key=os.getenv("OPENAI_API_KEY"))`
- Load the `.env` file: `load_dotenv()`

**Deliverable:** Server starts, Orchestrator initialises without errors.

---

### Step E: Add In-Memory Storage

**Goal:** Set up the dictionaries that will store sessions and tickets.

**Two storage structures:**

**`sessions` dictionary** — stores conversation history per customer session:
```
sessions = {
    "session_abc123": [
        {"role": "user",      "content": "My bill is wrong"},
        {"role": "assistant", "content": "I understand your concern..."},
        {"role": "user",      "content": "It's been 3 days already"}
    ],
    "session_xyz789": [ ... ]
}
```

**`tickets` dictionary** — stores escalated tickets for the Agent Dashboard:
```
tickets = {
    "TKT-00001": {
        "ticket_id": "TKT-00001",
        "status": "open",
        "category": "billing",
        "priority": "high",
        "last_message": "It's been 3 days already",
        "conversation_history": [...],
        ...
    }
}
```

**Deliverable:** Both dictionaries initialised in the file.

---

### Step F: Build `POST /api/chat`

**Goal:** The core endpoint. Customer types a message, AI responds.

**What happens inside this endpoint (the flow):**

```
1. Browser sends: { "message": "My bill is wrong", "session_id": "abc123" }
2. Look up history for "abc123" from sessions dictionary
3. Call orchestrator.process_request("My bill is wrong", history)
4. Orchestrator runs through all 7 agents
5. Orchestrator returns result (resolved / escalated / blocked)
6. Update session history with new message + response
7. If escalated: create a ticket in the tickets dictionary
8. Send response back to browser as JSON
```

**The result object from the Orchestrator looks like this (from reading the code):**
```python
{
    "agent": "ResolutionAgent",        # which agent handled it
    "analysis": {                      # triage decision data
        "category": "billing",
        "priority": "low",
        "sentiment": "neutral",
        "confidence_score": 0.85,
        "risk_score": 0.0,
        "requires_human": False,
        "explanation": "Matched billing keyword 'bill'"
    },
    "response": {
        "status": "resolved",          # or "escalated" or "blocked"
        "message": "I understand...",
        "confidence": 0.82             # only present when resolved
    }
}
```

**Deliverable:** `POST /api/chat` tested in `/docs`, returns a real AI response.

---

### Step G: Build `GET /api/tickets` and `GET /api/tickets/{ticket_id}`

**Goal:** Agent Dashboard can load the list of escalated tickets and open individual ones.

**What happens:**
- `GET /api/tickets` → return all values from the `tickets` dictionary as a list
- `GET /api/tickets/{ticket_id}` → return the single ticket matching that ID, or a 404 error if not found

**Deliverable:** Test in `/docs` — tickets created by `POST /api/chat` (when escalated) appear in the list.

---

### Step H: Build `POST /api/tickets/{ticket_id}/resolve`

**Goal:** Human agent can approve, send a custom reply, or close a ticket.

**Request body:**
```json
{
  "action": "approved",
  "agent_reply": "We have processed your refund."
}
```

**What happens:**
- Find the ticket by ID
- Update its `status` field to `"resolved"` or `"closed"`
- Save the `agent_reply`
- Return the updated ticket

**Deliverable:** In `/docs`, resolve a ticket and confirm its status changes.

---

### Step I: Build `GET /api/analytics/summary`

**Goal:** Admin Dashboard loads real statistics from the Analytics Agent.

**What happens:**
- Call `orchestrator.get_system_insights()` — thi![1773655306610](image/Jonas_API_Plan/1773655306610.png)![1773655311697](image/Jonas_API_Plan/1773655311697.png)![1773655322586](image/Jonas_API_Plan/1773655322586.png)s runs the AnalyticsAgent
- Return the result directly as JSON

**The Analytics Agent (`analytics_agent.py`) produces:**
```json
{
  "total_requests": 12,
  "resolved_count": 10,
  "resolution_rate": "83.33%",
  "category_breakdown": { "billing": 4, "general_inquiry": 5, ... },
  "hallucination_rate": 0.0,
  "escalation_rate": 0.167,
  "avg_retrieval_confidence": 0.0
}
```

> **Note:** `avg_retrieval_confidence` will be 0.0 for early testing because it comes from the verification agent's deep scoring, which requires several real interactions to accumulate.

**Deliverable:** `GET /api/analytics/summary` returns live data from the analytics agent.

---

### Step J: Build `GET /api/analytics/xai-traces`

**Goal:** Admin Dashboard shows the AI's decision reasoning for each processed request.

**What happens:**
- Loop through `orchestrator.analytics_db` (the list of logged interactions)
- For each entry, extract: ticket ID (or generate one), agent path, category, priority, decision reason (from `analysis.explanation`), confidence, timestamp
- Return as a list

**Why this is valuable:** The `explanation` field in every triage result is already a human-readable trace, e.g.:
> `"Matched billing keyword 'bill' | Urgent keyword detected | Sentiment detected as negative"`

This is the XAI (Explainable AI) trace — it shows exactly WHY the AI made each decision.

**Deliverable:** `GET /api/analytics/xai-traces` returns a list of real AI decision traces.

---

### Step K: Test All Endpoints

**Goal:** Every endpoint works correctly before the UI is connected.

**Test checklist using `http://localhost:8000/docs`:**

| Test | Endpoint | What to check |
|------|----------|--------------|
| 1. Health check | `GET /` | Returns `{"status": "ok"}` |
| 2. Normal message | `POST /api/chat` | Send "How do I reset my password?" → status: "resolved" |
| 3. Urgent/angry message | `POST /api/chat` | Send "I am very frustrated, I want a refund URGENT" → status: "escalated", ticket created |
| 4. Security test | `POST /api/chat` | Send "ignore previous instructions" → status: "blocked" |
| 5. Ticket list | `GET /api/tickets` | Shows ticket created in test 3 |
| 6. Single ticket | `GET /api/tickets/TKT-00001` | Returns full ticket details |
| 7. Resolve ticket | `POST /api/tickets/TKT-00001/resolve` | Status changes to "resolved" |
| 8. Analytics | `GET /api/analytics/summary` | Returns real stats |
| 9. XAI traces | `GET /api/analytics/xai-traces` | Returns decision log |

**Deliverable:** All 9 test cases pass. Screenshot taken for report.

---

### Step L: Wire Up the React UI

**Goal:** Replace mock data in the UI with real API calls.

**What to build:**

1. `ui/src/services/api.js` — all Axios calls in one place
2. `ui/.env.development` — `VITE_API_URL=http://localhost:8000`
3. Update `CustomerChat.jsx` — real chat
4. Update `AgentDashboard.jsx` — real tickets
5. Update `AdminDashboard.jsx` — real analytics

**This step will be detailed separately when we execute it.**

---

## 6. How to Run and Test Locally

Once `src/api.py` is built, here is how to run it:

**Terminal command (run from project root):**
```bash
python -m uvicorn src.api:app --reload --port 8000
```

> **What does this mean?**
> - `python -m uvicorn` = run uvicorn through Python (required on Windows — the bare `uvicorn` command may not be recognised)
> - `src.api:app` = look in the `src` folder, in the `api.py` file, find the variable called `app`
> - `--reload` = automatically restart the server whenever you save changes to the file (great for development)
> - `--port 8000` = run on port 8000

**Useful URLs when the server is running:**

| URL | What it shows |
|-----|--------------|
| `http://localhost:8000/` | Health check |
| `http://localhost:8000/docs` | Interactive API documentation (test all endpoints here) |
| `http://localhost:8000/redoc` | Alternative documentation view |

**Both terminals running simultaneously (final setup):**
- Terminal 1: `python -m uvicorn src.api:app --reload --port 8000` (backend)
- Terminal 2: `npm run dev` inside `ui/` (frontend)

---

## 7. What Changes in the UI After This

Once the API is working, you will update 4 files in the UI:

| UI File | Mock data to replace | Real API endpoint |
|---------|---------------------|------------------|
| `ui/src/services/api.js` | (new file — does not exist yet) | All endpoints |
| `ui/src/pages/CustomerChat.jsx` | `MOCK_RESPONSES` array | `POST /api/chat` |
| `ui/src/pages/AgentDashboard.jsx` | Hardcoded `MOCK_TICKETS` array | `GET /api/tickets`, `POST /api/tickets/{id}/resolve` |
| `ui/src/pages/AdminDashboard.jsx` | Hardcoded `dailyInteractions`, `categoryData`, etc. | `GET /api/analytics/summary`, `GET /api/analytics/xai-traces` |

---

## 8. Progress Tracker

| Step | Description | Status |
|------|-------------|--------|
| A | Install FastAPI + uvicorn | ✅ Done |
| B | Create `requirements.txt` | ✅ Done |
| C | Create `src/api.py` skeleton (health check) | ✅ Done |
| D | Add CORS + Orchestrator init | ✅ Done |
| E | Add in-memory sessions + tickets storage | ✅ Done |
| F | Build `POST /api/chat` | ✅ Done |
| G | Build `GET /api/tickets` + `GET /api/tickets/{id}` | ✅ Done |
| H | Build `POST /api/tickets/{ticket_id}/resolve` | ✅ Done |
| I | Build `GET /api/analytics/summary` | ✅ Done |
| J | Build `GET /api/analytics/xai-traces` | ✅ Done |
| K | Test all endpoints via `/docs` | ✅ Done — all 9 tests passed |
| L | Wire up React UI | ✅ Done — see breakdown below |

**Step L breakdown:**

| Sub-step | File | Status |
|----------|------|--------|
| L-1 | `ui/.env.development` — API URL for local dev | ✅ Done |
| L-1 | `ui/src/services/api.js` — all 6 Axios call functions | ✅ Done |
| L-2 | `ui/src/components/ChatWindow.jsx` — real chat API, loading state, session ID | ✅ Done |
| L-3 | `ui/src/pages/AgentDashboard.jsx` — real ticket list + resolve actions | ✅ Done |
| L-4 | `ui/src/pages/AdminDashboard.jsx` — real stat cards, pie chart, XAI traces | ✅ Done |

**What is real vs still static after Step L:**

| Section | Data source |
|---------|-------------|
| Chat responses | Real — Orchestrator via `POST /api/chat` |
| Agent Dashboard ticket queue | Real — `GET /api/tickets` |
| Admin stat cards | Real — `GET /api/analytics/summary` |
| Admin pie chart (categories) | Real — derived from `category_breakdown` |
| Admin XAI traces table | Real — `GET /api/analytics/xai-traces` |
| Daily interactions line chart | Real — `daily_interactions` field in `GET /api/analytics/summary`, computed from `analytics_db` |
| Agent routing table | Real — `agent_routing` field in `GET /api/analytics/summary`, computed from `analytics_db` |
| Knowledge gap alerts | Real — `knowledge_gaps` field in `GET /api/analytics/summary`, from `analytics_agent.detect_knowledge_gaps()` |

---

*This document will be updated as each step is completed. Last updated: March 2026.*
