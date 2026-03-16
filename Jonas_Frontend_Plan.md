# Frontend & UI Development Plan
## AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI Lead)
**Date:** 2026-03-05
**Status:** Complete (integration done — see `Jonas_Integration_Plan.md` and `QUICKSTART.md`)

---

## 1. Overview & Your Role

The project calls for a **3-tier UI Prototype** (from the Project Proposal, Phase 5). This means you need to build **three separate dashboards**, each serving a different type of user:

| Dashboard | User | Purpose |
|---|---|---|
| **Customer Portal** | End customer | Chat with the AI support system |
| **Support Agent Dashboard** | Human support agent | Review escalated cases (Human-in-the-Loop) |
| **AI Admin Dashboard** | AI system admin | Monitor analytics, XAI traces, system health |

Your frontend will connect to the Python backend (orchestrator + agents) via a **REST API** that the team will build. Think of it like this: the backend "thinks", the API is the "translator", and your frontend is the "face" the users see.

---

## 2. Recommended Technology Stack

### Why this stack?
Given your non-technical background, the goal is to use tools that:
- Are widely used (lots of tutorials / community help)
- Are cloud-deployable with minimal effort
- Have ready-made visual components (so you don't build from scratch)

### The Stack

```
[User's Browser]
      |
      | (HTTP Requests)
      v
[Frontend: React + Vite]          <-- You build this
      |
      | (REST API calls)
      v
[Backend API: FastAPI (Python)]   <-- Your teammates build this
      |
      v
[AI Agents / Orchestrator]        <-- Already being built by team
```

| Layer | Technology | Why |
|---|---|---|
| **Frontend Framework** | React (with Vite) | Industry standard, huge community, easy to deploy |
| **UI Component Library** | Ant Design (antd) | Ready-made enterprise components (tables, charts, chat) |
| **Language** | JavaScript (or TypeScript) | TypeScript is safer, JavaScript is simpler to start |
| **Charting** | Recharts or Ant Design Charts | For admin analytics graphs |
| **HTTP Client** | Axios | Easy API calls to backend |
| **Routing** | React Router | Navigate between dashboards |
| **Deployment** | Vercel (frontend) | Free, 1-click deploy from GitHub |
| **Backend API** | FastAPI (Python) | Your teammates' domain; you just consume it |

### Alternatives if React feels too hard:
- **Streamlit** (Python-only, much simpler, but looks less professional)
- **Gradio** (designed for AI demos, very quick to set up)
- Use Streamlit for the prototype, then migrate to React later

> **Recommendation for now:** Start with React + Ant Design. It looks professional and is deployable to any cloud. If you hit a wall, fall back to Streamlit.

---

## 3. The Three Dashboards — What to Build

### Dashboard 1: Customer Chat Portal

**Who uses it:** The customer submitting a support request.

**Key features:**
- Clean, modern chat interface (like a chatbot widget)
- Send a message → receive AI response
- Show which agent handled it (e.g., "Handled by: Resolution Agent")
- Show priority/sentiment ("High Priority", "Frustrated Tone")
- Option to escalate to a human ("Talk to a human")
- Chat history display

**Visual concept:**
```
+------------------------------------------+
|  Acme Corp Support          [x] Minimize |
+------------------------------------------+
|  Hello! How can I help you today?        |
|                                          |
|  [AI]  Your order is being processed.   |
|        Estimated delivery: 3-5 days.    |
|                                          |
|  [You] I want to speak to a human.      |
|                                          |
|  [AI]  Escalating to a support agent... |
+------------------------------------------+
| Type your message...          [Send]     |
+------------------------------------------+
```

---

### Dashboard 2: Support Agent Dashboard (HITL)

**Who uses it:** Human support staff who handle escalated cases.

**Key features:**
- Queue/list of escalated tickets (with priority, sentiment, timestamp)
- Click a ticket → see full conversation history
- AI-generated summary of the issue (auto-populated)
- Action panel: Approve AI response / Write custom reply / Close ticket
- Status badges (Open, In Progress, Resolved)

**Visual concept:**
```
+--------------------+-----------------------------+
| TICKET QUEUE       |  TICKET: TKT-12345          |
|--------------------|                             |
| TKT-12345 [HIGH]   |  Customer: Jane Doe         |
| TKT-12346 [MED]    |  Sentiment: Frustrated      |
| TKT-12347 [LOW]    |  Category: Billing          |
|                    |-----------------------------|
|                    |  Conversation History:      |
|                    |  User: I was charged twice! |
|                    |  AI: I understand...        |
|                    |-----------------------------|
|                    |  AI Summary: Customer       |
|                    |  reports double billing.    |
|                    |-----------------------------|
|                    |  [Approve] [Reply] [Close]  |
+--------------------+-----------------------------+
```

---

### Dashboard 3: AI Admin Dashboard

**Who uses it:** The AI/system administrator monitoring the system.

**Key features:**
- Summary cards (Total interactions, Avg resolution time, Escalation rate)
- Bar/line chart of interactions over time
- Pie chart of request categories (billing, technical, general)
- Agent routing table — shows where tickets are routed *after* Triage (the 3 "destination" agents)
- XAI section: Decision trace logs (chain-of-thought, per ticket)
- Knowledge gap alerts ("Users frequently ask about X, but we have no answer")

> **Note on the 7 agents:** All 7 agents from the proposal are active, but they play different roles in the pipeline.
> - **Always run on every request (background):** Security & Compliance Agent, Verification Agent, Analytics & Feedback Agent
> - **Triage always runs first:** Triage Agent (100% of requests)
> - **Routing destinations (one of these handles each ticket):** Resolution Agent, Information Retrieval Agent, Escalation Agent
>
> The routing table below tracks the 3 destination agents. The background agents are shown separately as pipeline health indicators.

**Visual concept:**
```
+--------------------------------------------------+
|  AI ADMIN DASHBOARD                              |
+--------------------------------------------------+
| [157 Interactions] [92% Resolved] [8% Escalated]|
+--------------------------------------------------+
|   Interactions This Week        |  By Category  |
|   [LINE CHART: Mon-Sun]         |  [PIE CHART]  |
+--------------------------------------------------+
|   Routing (post-Triage)         |  Knowledge    |
|   Resolution Agent:    45%      |  Gaps         |
|   Info Retrieval (RAG): 30%     |  - "Refund"   |
|   Escalation Agent:     8%      |  - "API key"  |
|   (Remaining: re-tried/pending) |               |
+--------------------------------------------------+
|   Background Agent Health                       |
|   Security Agent: Active | Verification: Active |
|   Analytics Agent: Active                       |
+--------------------------------------------------+
|   XAI Decision Traces                           |
|   TKT-12345: "Classified as billing due to..."  |
+--------------------------------------------------+
```

---

## 4. How the Frontend Talks to the Backend

Your backend team will expose a **REST API**. You will use **Axios** (a JavaScript library) to call these endpoints. Here are the API endpoints you should ask your teammates to build:

| Endpoint | Method | Purpose | You Call From |
|---|---|---|---|
| `/api/chat` | POST | Send customer message, get AI reply | Customer Portal |
| `/api/tickets` | GET | Fetch list of escalated tickets | Agent Dashboard |
| `/api/tickets/{id}` | GET | Fetch one ticket's conversation | Agent Dashboard |
| `/api/tickets/{id}/resolve` | POST | Human agent resolves a ticket | Agent Dashboard |
| `/api/analytics/summary` | GET | Total stats (interactions, etc.) | Admin Dashboard |
| `/api/analytics/trends` | GET | Time-series data for charts | Admin Dashboard |
| `/api/analytics/xai-traces` | GET | XAI decision logs | Admin Dashboard |

> **Important:** Until the backend team is ready, you can use **mock data** in your frontend — hard-code fake responses. This lets you build the UI independently.

---

## 5. Cloud Deployment Plan

### Frontend Deployment (Vercel — Recommended for Start)
Vercel connects to your GitHub repository and auto-deploys on every push. It's free, fast, and easy.

```
GitHub Repo → Vercel → https://your-app.vercel.app
```

### Full Cloud Options (Later, for Production)

| Cloud | Frontend | Backend API | Notes |
|---|---|---|---|
| **AWS** | S3 + CloudFront | EC2 / ECS / Lambda | Most flexible, most complex |
| **Azure** | Azure Static Web Apps | Azure App Service | NCS/enterprise friendly |
| **GCP** | Firebase Hosting | Cloud Run | Good free tier |
| **Vercel + Render** | Vercel (free) | Render.com (free tier) | Easiest for student projects |

**Recommendation for this project:**
1. **Prototype phase:** Deploy frontend to Vercel, backend to Render.com
2. **Final submission:** Migrate to Azure (NCS-aligned) if required

---

## 6. Step-by-Step Learning & Building Roadmap

This is your personal action plan. Take it one step at a time.

### Phase A: Learn the Basics (1 week)
1. **HTML & CSS basics** — Understand how web pages are structured
   - Resource: [freeCodeCamp HTML/CSS](https://www.freecodecamp.org/learn/2022/responsive-web-design/)
2. **JavaScript basics** — Variables, functions, arrays, fetch API
   - Resource: [JavaScript.info](https://javascript.info/) (Chapters 1-5)
3. **React fundamentals** — Components, props, state, useEffect
   - Resource: [Official React tutorial](https://react.dev/learn)

### Phase B: Project Setup (1-2 days)
```bash
# Install Node.js from nodejs.org first, then:
npm create vite@latest ui -- --template react
cd ui
npm install
npm run dev   # Opens browser at localhost:5173
```

Then install component libraries:
```bash
npm install antd axios react-router-dom recharts
```

### Phase C: Build Mock UI (1-2 weeks)
- Set up routing between 3 dashboards
- Build Customer Chat page with mock AI responses
- Build Agent Dashboard with hardcoded ticket data
- Build Admin Dashboard with hardcoded charts

### Phase D: Connect to Backend API (1 week, coordinate with team)
- Replace mock data with real API calls using Axios
- Handle loading states and errors
- Test with real backend

### Phase E: Deploy (1-2 days)
- Push code to GitHub
- Connect GitHub to Vercel
- Configure environment variables (API URL)
- Test live deployment

---

## 7. Project Folder Structure

Your UI code will live in a `ui/` folder in the project repo:

```
nus_ai_team_4_2026/
├── src/                              # Backend Python code
│   ├── agents/                       #   All 7 agent files (teammates' code)
│   ├── orchestrator.py               #   Main pipeline — routes messages through agents
│   ├── main.py                       #   Original CLI entry point
│   └── api.py                        # ✅ Step L — NEW: FastAPI web server Jonas built.
│                                     #            Wraps the Orchestrator as HTTP endpoints.
│                                     #            Run: python -m uvicorn src.api:app --reload
│
├── tests/                            # Backend automated tests
├── docs/                             # Project documentation (XAI, Cybersecurity reports)
│
├── requirements.txt                  # ✅ Step B — NEW: Python dependency list.
│                                     #            Run `pip install -r requirements.txt` to
│                                     #            install all backend libraries at once.
│
├── .env                              # ✅ Secured — OpenAI API key (gitignored — never committed).
│
├── ui/                               # YOUR FOLDER — everything frontend lives here
│   │
│   ├── index.html                    # ✅ Step 1 — The single HTML page the browser loads.
│   │                                 #            It contains a <div id="root"> where React
│   │                                 #            injects the entire application.
│   │
│   ├── vite.config.js                # ✅ Step 1 — Configuration for the Vite build tool.
│   │                                 #            Tells Vite to use the React plugin and
│   │                                 #            which port to run the dev server on (5173).
│   │
│   ├── package.json                  # ✅ Step 1 — The project's "ingredient list". Lists every
│   │                                 #            library (antd, axios, etc.) and the npm scripts
│   │                                 #            (dev, build, preview).
│   │
│   ├── .gitignore                    # ✅ Step 1 — Tells Git which folders/files to never commit.
│   │                                 #            Excludes node_modules (too large) and
│   │                                 #            .env files (contain secrets).
│   │
│   ├── .env.development              # ✅ Step L — NEW: Frontend environment config for local dev.
│   │                                 #            Sets VITE_API_URL=http://localhost:8000 so
│   │                                 #            Axios knows where the FastAPI server is.
│   │                                 #            Gitignored — production URL set in Vercel dashboard.
│   │
│   └── src/                          #            All source code you write lives here.
│       │
│       ├── main.jsx                  # ✅ Step 1 — The app's ignition switch. Finds the
│       │                             #            <div id="root"> in index.html and mounts
│       │                             #            the React app into it. You rarely edit this.
│       │
│       ├── App.jsx                   # ✅ Step 3 — Updated to wrap all pages in the Layout shell
│       │                             #            (ConfigProvider + Layout + NavBar + Content).
│       │
│       ├── index.css                 # ✅ Step 1 — Global stylesheet applied to the entire app.
│       │                             #            Resets browser default margins/padding so
│       │                             #            all pages start from a clean slate.
│       │
│       ├── pages/                    #            One file per dashboard. Each file is a full
│       │   │                         #            page that React Router switches between.
│       │   ├── CustomerChat.jsx      # ✅ Step 4 — Dashboard 1: customer-facing chat portal.
│       │   │                         #            Updated Step L: uses real API, session ID,
│       │   │                         #            loading spinner while AI responds.
│       │   ├── AgentDashboard.jsx    # ✅ Step 5 — Dashboard 2: human agent's ticket queue.
│       │   │                         #            Updated Step L: loads real tickets on mount,
│       │   │                         #            resolve/reply/close actions call the API.
│       │   └── AdminDashboard.jsx    # ✅ Step 6 — Dashboard 3: analytics and AI monitoring.
│       │                             #            Updated Step L: real stat cards, real pie chart
│       │                             #            (category_breakdown), real XAI traces table.
│       │
│       ├── components/               #            Reusable UI building blocks shared across pages.
│       │   │                         #            Think of these as LEGO bricks — built once,
│       │   │                         #            used wherever needed.
│       │   ├── NavBar.jsx            # ✅ Step 3 — The top navigation bar with links to all 3
│       │   │                         #            dashboards. Wraps every page.
│       │   ├── ChatWindow.jsx        # ✅ Step 4 — The chat bubble UI (message list + input box).
│       │   │                         #            Updated Step L: calls POST /api/chat, manages
│       │   │                         #            session ID, shows "AI is thinking..." spinner.
│       │   └── TicketCard.jsx        # ✅ Step 5 — A single ticket summary card (ID, priority,
│       │                             #            sentiment badge). Used in AgentDashboard.jsx.
│       │
│       └── services/                 #            Code that talks to the outside world (the API).
│           │                         #            Kept separate so API logic never mixes with
│           │                         #            visual/display code.
│           └── api.js                # ✅ Step L — NEW: All 6 Axios API call functions.
│                                     #            sendChatMessage(), getTickets(), resolveTicket(),
│                                     #            getAnalyticsSummary(), getXaiTraces(), etc.
│
├── Jonas_Frontend_Plan.md            # UI planning document (this file)
├── Jonas_Integration_Plan.md         # Integration architecture, API contract, completion status
├── Jonas_API_Plan.md                 # Step-by-step guide for building src/api.py
├── Jonas_Design_Decisions.md         # ✅ NEW: Intentional design choices and known behaviours
└── QUICKSTART.md                     # ✅ NEW: Step-by-step guide for running the project locally
```

> **Legend:** ✅ Done &nbsp;|&nbsp; ⬜ Planned (step number shown)

---

## 8. Key Things to Discuss With Your Team

Before you build, align with your teammates on:

1. **API contract** — What exactly will each API endpoint return? Ask them to share the response format (JSON structure) so you can build mock data matching it.
2. **Authentication** — Will there be login? (Probably not for a prototype, but clarify)
3. **Backend URL** — What is the URL of the backend API? (localhost during dev, a cloud URL in prod)
4. **Data refresh** — Does the admin dashboard need real-time updates, or is polling every 30 seconds fine?
5. **Ticket creation flow** — When does the escalation agent create a ticket? You need to know when to fetch new tickets.

---

## 9. Tools You'll Need on Your Machine

| Tool | Purpose | Where to Get |
|---|---|---|
| **Node.js (v20+)** | Run JavaScript/React locally | https://nodejs.org |
| **VS Code** | Code editor (already installed) | - |
| **Git** | Version control (already set up) | - |
| **Postman** | Test API calls before connecting to UI | https://www.postman.com |
| **Chrome DevTools** | Debug your web app | Built into Chrome (F12) |

---

## 10. Summary — Current Status

**UI development and API integration are complete.** All three dashboards are built and connected to the real Orchestrator backend.

**Remaining before final submission:**

1. **Cloud deployment** — Deploy backend to Azure, frontend to Vercel. See `Jonas_Integration_Plan.md` Section 10 for options.
2. **Security check** — Confirm `.env` files are git-ignored and the OpenAI API key is not committed. See `Jonas_Integration_Plan.md` Section 12.
3. **Team testing** — Share `QUICKSTART.md` with all teammates so they can run the full system locally and verify end-to-end.

---

*This plan will be updated as development progresses and backend API details are confirmed.*

---

## 11. Structured Development Roadmap

> This is the step-by-step build sequence. Each step has a clear goal and defined deliverable.
> Steps 1–6 are fully independent of the backend team — you can complete them on your own.
> Steps 7–10 require coordination with teammates.

---

### Step 1: Environment Setup
**Goal:** Get your machine ready to write and run a React application locally.

**What you will do:**
- Install Node.js (v20 LTS) from nodejs.org
- Verify installation in terminal: `node -v` and `npm -v`
- Create the React project using Vite inside the `ui/` folder
- Install the required libraries: Ant Design, Axios, React Router, Recharts
- Run the default starter app and confirm it opens in your browser at `localhost:5173`

**Deliverable:** A blank React app running locally with all libraries installed. No real content yet — just the starter screen.

**Files created in Step 1:**
```
ui/
├── index.html          ← The HTML entry point (browser loads this first)
├── vite.config.js      ← Tells Vite how to run and build the app
├── package.json        ← Lists all libraries the project depends on
├── .gitignore          ← Tells Git to ignore node_modules and build output
└── src/
    ├── main.jsx        ← Boots the React app (attaches it to index.html)
    ├── App.jsx         ← Root component — shows the Step 1 confirmation screen
    └── index.css       ← Base global styles (resets browser defaults)
```

**Libraries installed (via `npm install`):**

| Library | Purpose |
|---|---|
| `react` + `react-dom` | The core React framework |
| `antd` (Ant Design) | Ready-made professional UI components |
| `react-router-dom` | Navigation between the 3 dashboard pages |
| `axios` | Makes API calls to the Python backend |
| `recharts` | Draws charts (line, pie) for the Admin Dashboard |
| `vite` + `@vitejs/plugin-react` | Dev tools: runs the local server and builds for production |

---

### Step 2: Project Structure & Routing
**Goal:** Set up the folder layout and connect the three dashboards with navigation routes.

**What you will do:**
- Create the `pages/`, `components/`, and `services/` folders inside `ui/src/`
- Create three empty placeholder page files: `CustomerChat.jsx`, `AgentDashboard.jsx`, `AdminDashboard.jsx`
- Set up React Router so that each URL path loads the right page:
  - `/` → Customer Chat Portal
  - `/agent` → Support Agent Dashboard
  - `/admin` → AI Admin Dashboard
- Confirm you can navigate between the three blank pages via the URL bar

**Deliverable:** Three navigable (but empty) pages reachable by URL. No content yet.

---

### Step 3: Navigation Shell & Layout
**Goal:** Build the visual frame that all three dashboards sit inside — the top navigation bar and page layout.

**What you will do:**
- Build a `NavBar.jsx` component using Ant Design's `Menu` component
- The nav bar links to all three dashboards (Customer, Agent, Admin)
- Wrap all pages in a consistent layout (header + content area)
- Apply a basic colour theme consistent with a professional support system (e.g., blue/white)

**Deliverable:** All three pages now have a shared top navigation bar. You can click between dashboards. Content areas are still empty.

---

### Step 4: Customer Chat Portal (Mock Data)
**Goal:** Build a working chat interface that simulates a conversation with the AI — using hardcoded fake responses, no real backend needed.

**What you will do:**
- Build a `ChatWindow.jsx` component: message list + text input + send button
- On "Send", append the user message to the chat and immediately show a hardcoded AI reply
- Display the handling agent name and classification (e.g., "Handled by: Resolution Agent | Priority: High")
- Add a basic "Escalate to human" button that shows a confirmation message
- Style it to look like a chat widget (bubbles, timestamps)

**Deliverable:** A fully interactive-looking chat page. Users can type messages and see mock AI replies. No real API calls yet.

---

### Step 5: Support Agent Dashboard (Mock Data)
**Goal:** Build the ticket queue and detail panel for human agents to review and act on escalated cases, using hardcoded ticket data.

**What you will do:**
- Create a `TicketCard.jsx` component to display one ticket in the queue (ticket ID, customer name, priority badge, sentiment, timestamp)
- Build the left panel: a list of 3–5 hardcoded mock tickets
- Build the right panel: when a ticket is clicked, show full conversation history, AI-generated summary, and category
- Add three action buttons: **Approve AI Response**, **Write Custom Reply**, **Close Ticket**
- Clicking an action updates the ticket status badge (Open → Resolved)

**Deliverable:** A two-panel layout where clicking a ticket from the queue loads its detail view. Actions work visually (status changes), no backend yet.

---

### Step 6: AI Admin Dashboard (Mock Data) ✅
**Goal:** Build the analytics and monitoring view with charts and system health indicators, using hardcoded data.

**What you will do:**
- Build the top summary row: 3–4 metric cards (Total Interactions, Resolved %, Escalation Rate, Avg Response Time)
- Build a line chart (using Recharts) showing interactions per day over the last 7 days — hardcoded numbers
- Build a pie chart showing request categories (billing, technical, general, other) — hardcoded percentages
- Build the Agent Routing table: showing Resolution Agent, Info Retrieval Agent, and Escalation Agent percentages
- Build the Background Agent Health row: Security Agent, Verification Agent, Analytics Agent — all showing "Active"
- Build the XAI Decision Traces section: a table of 3–5 hardcoded trace entries (ticket ID, decision reason, timestamp)
- Build the Knowledge Gaps section: a list of hardcoded alert items

**Deliverable:** A visually complete analytics dashboard with working charts and tables — all data is fake/hardcoded, but it looks and behaves like a real dashboard.

---

### Step 7: Backend API Integration
**Goal:** Replace all hardcoded mock data with real data from the team's Python backend API.

**Prerequisites:** Teammates have deployed the FastAPI backend and shared the API base URL.

**What you will do:**
- Create `ui/src/services/api.js` — a single file containing all Axios API call functions
- Replace mock chat responses with calls to `POST /api/chat`
- Replace mock ticket list with calls to `GET /api/tickets` and `GET /api/tickets/{id}`
- Wire agent actions to `POST /api/tickets/{id}/resolve`
- Replace mock analytics numbers with calls to `GET /api/analytics/summary` and `/trends`
- Replace mock XAI traces with calls to `GET /api/analytics/xai-traces`
- Add loading spinners while API calls are in progress
- Add error messages if an API call fails

**Deliverable:** All three dashboards now show real, live data from the backend. The system works end-to-end.

---

### Step 8: Styling & Polish
**Goal:** Make the application look complete and professional before final submission.

**What you will do:**
- Ensure the layout is responsive (looks reasonable on different screen sizes)
- Review all pages for visual consistency (fonts, colours, spacing)
- Add the project/company name and logo to the NavBar
- Add empty state messages (e.g., "No escalated tickets at the moment" when the queue is empty)
- Confirm all buttons give user feedback (disable on click, show success/error message)
- Fix any visual bugs noticed during end-to-end testing

**Deliverable:** A polished, submission-ready UI with consistent styling and no obvious visual issues.

---

### Step 9: End-to-End Testing
**Goal:** Verify that the full system works correctly from the browser to the backend before deployment.

**What you will do:**
- Manually walk through each user journey:
  - Customer submits a query → sees a response → escalates to human
  - Agent views escalated ticket → approves response → ticket closes
  - Admin views analytics → drills into XAI trace
- Test with the backend turned off — confirm error messages appear gracefully
- Test in Chrome and Edge browsers
- Flag any issues to the team for backend fixes

**Deliverable:** A tested, stable application with known issues documented.

---

### Step 10: Cloud Deployment
**Goal:** Make the application accessible via a public URL on the internet.

**What you will do:**
- Push the final `ui/` code to the shared GitHub repository
- Connect the repository to Vercel (or agreed cloud platform)
- Configure the environment variable `VITE_API_URL` to point to the live backend URL
- Trigger a deployment and verify the live URL works
- Share the URL with the team for final integration testing

**Deliverable:** A live, publicly accessible URL for the application. Ready for demo and project submission.

---

### Step Summary

| Step | Name | Depends On Backend? | Est. Effort |
|---|---|---|---|
| 1 | Environment Setup | No | 2–3 hours |
| 2 | Project Structure & Routing | No | 2–3 hours |
| 3 | Navigation Shell & Layout | No | 3–4 hours |
| 4 | Customer Chat Portal (Mock) | No | 6–8 hours |
| 5 | Agent Dashboard (Mock) | No | 6–8 hours |
| 6 | Admin Dashboard (Mock) | No | 8–10 hours |
| 7 | Backend API Integration | **Yes** | 6–8 hours |
| 8 | Styling & Polish | No | 4–6 hours |
| 9 | End-to-End Testing | **Yes** | 3–4 hours |
| 10 | Cloud Deployment | **Yes** | 2–3 hours |
| | **Total** | | **~42–57 hours** |

