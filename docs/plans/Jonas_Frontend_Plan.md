# Frontend & UI Development Plan
## AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI Lead)
**Date:** 2026-03-05
**Last Updated:** 25 Mar 2026
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
│       │                             #            Updated Step L: real stat cards, pie chart,
│       │                             #            XAI traces, daily interactions chart, agent
│       │                             #            routing table, knowledge gap alerts — all live.
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
│       ├── services/                 #            Code that talks to the outside world (the API).
│       │   │                         #            Kept separate so API logic never mixes with
│       │   │                         #            visual/display code.
│       │   └── api.js                # ✅ Step L — NEW: All 6 Axios API call functions.
│       │                             #            sendChatMessage(), getTickets(), resolveTicket(),
│       │                             #            getAnalyticsSummary(), getXaiTraces(), etc.
│       │
│       └── utils/                    #            Shared helper functions used across multiple
│           │                         #            pages and components.
│           └── formatters.js         # ✅ Step R — NEW: capitalize(), formatCategory(),
│                                     #            mapSentiment(). Extracted here to avoid
│                                     #            duplicating the same code in 3 different files.
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

**In progress — Phase 2: UI Enhancement** (see Section 11 below).

**Remaining before final submission:**

1. ~~**Phase 2 UI enhancements** — Dark/Light mode, glass effect, Atkinson Hyperlegible Next font.~~ ✅ Done (Steps M–T)
2. **Cloud deployment** — Deploy backend to Render/Azure, frontend to Vercel. See `DEPLOYMENT.md` for full instructions. Remember to set `INTERNAL_API_KEY` on the backend host and `VITE_INTERNAL_API_KEY` in Vercel.
3. ~~**Security check** — Confirm `.env` files are git-ignored and API key not committed.~~ ✅ Done (Step V — full API key auth implemented)
4. **Team testing** — Share `QUICKSTART.md` with all teammates so they can run the full system locally and verify end-to-end.

---

## 11. Phase 2: UI Enhancements

Three visual enhancements to be implemented after integration is complete.

---

### Enhancement 1 — Atkinson Hyperlegible Next Font

**Goal:** Replace the default system font with Atkinson Hyperlegible Next for maximum legibility across all three dashboards.

**What it is:** A typeface designed specifically for readers with low vision, developed by the Braille Institute. It maximises character distinction — every letter and number is designed to be unambiguous at any size.

**How to implement:**

**Step 1 — Load the font**

Add to `ui/index.html` inside `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;1,200;1,300;1,400;1,500;1,600;1,700;1,800&display=swap" rel="stylesheet">
```

> **Note:** If "Atkinson Hyperlegible Next" is not yet available on Google Fonts, use `family=Atkinson+Hyperlegible` (the original version) as a fallback — it is confirmed available. The "Next" variant may need to be self-hosted if not on Google Fonts at time of implementation.

**Step 2 — Apply globally via Ant Design token**

In `App.jsx`, add `fontFamily` to the Ant Design theme token:
```javascript
token: {
  fontFamily: "'Atkinson Hyperlegible Next', 'Atkinson Hyperlegible', sans-serif",
}
```

**Step 3 — Apply as CSS fallback**

In `ui/src/index.css`:
```css
body {
  font-family: 'Atkinson Hyperlegible Next', 'Atkinson Hyperlegible', sans-serif;
}
```

**Files changed:** `ui/index.html`, `ui/src/App.jsx`, `ui/src/index.css`

---

### Enhancement 2 — Dark Mode / Light Mode Toggle (OLED-compatible)

**Goal:** Let users switch between a light theme and a dark theme. Dark mode uses a tiered near-black colour system designed for comfort on OLED screens — avoiding both the grey glow of standard dark modes and the harsh halation of pure black + white text.

#### Why not pure black everywhere?

Pure `#000000` background with pure `#ffffff` text creates a 21:1 contrast ratio — technically the highest possible, but *too high* for comfortable reading. People with astigmatism (very common) experience a "halation" effect where white text on pure black appears to bleed or glow at the edges. WCAG AAA only requires 7:1 for good reason.

Apple, Google (Material Design), and Netflix all deliberately avoid pure black for content surfaces. The solution is to reduce contrast from **both ends simultaneously**: a near-black surface with off-white text.

#### Tiered dark mode colour system

| Surface | Colour | Purpose |
|---------|--------|---------|
| Page background (behind cards) | `#000000` | True OLED black — no content sits directly here; OLED pixels fully off in the gaps between cards |
| Card / panel surfaces | `#0d0d0d` | Near-black — just enough to visually separate card from background; glass layer sits on this |
| Elevated surfaces (modals, drawers) | `#1a1a1a` | Slightly lighter — creates depth hierarchy |
| Primary text | `#f0f0f0` | Off-white — reduces glare from both ends; contrast ratio ~17:1 on `#0d0d0d` — excellent but not harsh |
| Secondary / muted text | `#a0a0a0` | Comfortable for less important information |

> The glass effect in Step O naturally softens contrast further — translucent layers mean text never sits on bare `#000000`.

**How it works:**

Ant Design 5's `ConfigProvider` accepts a `theme` prop. Switching between `theme.defaultAlgorithm` (light) and `theme.darkAlgorithm` (dark) instantly re-themes every component — no per-component changes needed.

**Implementation steps:**

**Step 1 — Dark mode state in `App.jsx`**
```javascript
const [isDark, setIsDark] = useState(
  () => localStorage.getItem('theme') === 'dark'
)
```

**Step 2 — Pass tiered theme tokens to ConfigProvider**
```javascript
<ConfigProvider theme={{
  algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorBgBase:       isDark ? '#000000' : '#ffffff',  // page background (behind cards)
    colorBgContainer:  isDark ? '#0d0d0d' : '#ffffff',  // card / panel surfaces
    colorBgElevated:   isDark ? '#1a1a1a' : '#ffffff',  // modals / drawers
    colorText:         isDark ? '#f0f0f0' : '#1a1a1a',  // primary text (off-white in dark)
    colorTextSecondary:isDark ? '#a0a0a0' : '#595959',  // secondary text
    fontFamily: "'Atkinson Hyperlegible Next', 'Atkinson Hyperlegible', sans-serif",
  }
}}>
```

**Step 3 — Toggle button in `NavBar.jsx`**
- Add a sun/moon icon button (use Ant Design's `<Button>` with `SunOutlined` / `MoonOutlined` icons)
- On click: toggle `isDark` state and save to `localStorage`

**Step 4 — Sync body and html background**

In `index.css`, the area behind the app also needs to go true black (so no grey bleed at page edges):
```css
body {
  background-color: #000000;
  transition: background-color 0.3s ease;
}
```

**Files changed:** `ui/src/App.jsx`, `ui/src/components/NavBar.jsx`, `ui/src/index.css`

---

### Enhancement 3 — Glass Effect (iOS 26 / macOS 26 "Liquid Glass" Design Language)

**Goal:** Apply a frosted-glass visual treatment to cards, panels, and the navigation bar — consistent with Apple's 2026 design language (translucent backgrounds, backdrop blur, subtle borders).

**How it works:**

Glass effect is achieved with three CSS properties:
- `backdrop-filter: blur(20px) saturate(180%)` — blurs whatever is behind the element
- `background: rgba(...)` — translucent fill, not opaque
- `border: 1px solid rgba(...)` — thin bright border that catches light

The values change between light and dark mode via CSS custom properties (variables).

**CSS variables (applied in `index.css`):**
```css
/* Light mode glass */
:root {
  --glass-bg:           rgba(255, 255, 255, 0.65);
  --glass-border:       rgba(255, 255, 255, 0.55);
  --glass-shadow:       0 8px 32px rgba(0, 0, 0, 0.08);
  --glass-blur:         blur(20px) saturate(180%);
}

/* Dark / OLED mode glass */
[data-theme='dark'] {
  --glass-bg:           rgba(255, 255, 255, 0.05);
  --glass-border:       rgba(255, 255, 255, 0.10);
  --glass-shadow:       0 8px 32px rgba(0, 0, 0, 0.6);
}
```

**Ant Design token overrides** — override Card background to use glass:
```javascript
components: {
  Card: {
    colorBgContainer: 'var(--glass-bg)',
  },
  Layout: {
    headerBg: 'var(--glass-bg)',
  },
}
```

**Apply `data-theme` attribute** in `App.jsx` so CSS variables switch automatically:
```javascript
useEffect(() => {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}, [isDark])
```

**Files changed:** `ui/src/App.jsx`, `ui/src/index.css`

---

### Phase 2 Implementation Order

| Step | Enhancement | Files |
|------|-------------|-------|
| M | Atkinson Hyperlegible Next font | `index.html`, `App.jsx`, `index.css` |
| N | Dark / Light mode toggle + OLED tokens | `App.jsx`, `NavBar.jsx`, `index.css` |
| O | Glass effect CSS variables + token overrides | `App.jsx`, `index.css` |
| P | Dark mode & visual polish (all components) | `index.css`, `App.jsx`, `ChatWindow.jsx`, `TicketCard.jsx`, `AgentDashboard.jsx` |
| Q | True HITL + UX improvements | `src/orchestrator.py`, `src/api.py`, `AgentDashboard.jsx`, `ChatWindow.jsx` |
| R | Code cleanup & shared utilities | `ui/src/utils/formatters.js`, `AgentDashboard.jsx`, `ChatWindow.jsx`, `AdminDashboard.jsx`, `src/orchestrator.py`, `src/api.py` |
| S | Self-learning vector DB (approved answers) | `src/vector_db.py`, `src/api.py` |
| T | XAI traces, escalation UX, date format, knowledge gap bug fix | `src/agents/analytics_agent.py`, `src/agents/triage_agent.py`, `src/orchestrator.py`, `src/api.py`, `ui/src/utils/formatters.js`, `ChatWindow.jsx`, `AdminDashboard.jsx`, `AgentDashboard.jsx` |
| U | Simplify: color constants, single-pass analytics, named thresholds, action handler refactor | `ui/src/utils/formatters.js`, `ChatWindow.jsx`, `TicketCard.jsx`, `AgentDashboard.jsx`, `AdminDashboard.jsx`, `src/agents/analytics_agent.py`, `src/agents/escalation_agent.py`, `src/agents/resolution_agent.py`, `src/agents/triage_agent.py` |
| V | Security: API key authentication on agent and admin endpoints | `src/api.py`, `ui/src/services/api.js`, `.env`, `ui/.env.development` |

> Steps M, N, and O build on each other — do them in order. Step N sets up the `isDark` state and `data-theme` attribute that Step O relies on. Step P is a follow-up polish pass applied after visual testing. Step Q adds true HITL (AI draft generation) and UX polish. Step R is a code quality pass — no user-visible changes. Step S adds a self-learning feedback loop where human-approved ticket replies are stored in ChromaDB to improve future AI responses. Step T improves XAI explainability, escalation messaging, date formatting, and fixes a bug that prevented Knowledge Gap Alerts from appearing. Step U is a second code quality pass consolidating duplicate constants and simplifying state management — no user-visible changes. Step V adds API key authentication to all agent/admin endpoints.

---

### Phase 2 Progress Tracker

| Step | Description | Status |
|------|-------------|--------|
| M | Atkinson Hyperlegible Next font | ✅ Done |
| N | Dark / Light mode toggle (OLED-compatible) | ✅ Done |
| O | Glass effect (iOS/macOS 26 design language) | ✅ Done |
| P | Dark mode & visual polish | ✅ Done |
| Q | True HITL + UX improvements | ✅ Done |
| R | Code cleanup & shared utilities | ✅ Done |
| S | Self-learning vector DB (approved answers) | ✅ Done |
| T | XAI traces, escalation UX, date format, knowledge gap bug fix | ✅ Done |
| U | Simplify: color constants, single-pass analytics, named thresholds, action handler refactor | ✅ Done |
| V | Security: API key authentication on agent and admin endpoints | ✅ Done |

### Step P — Dark Mode & Visual Polish (Detail)

After visual testing of Steps M–O, the following refinements were applied:

| Area | Change |
|------|--------|
| Card opacity | Increased `Card.colorBgContainer` from `0.04` → `0.14` so sections are visible on OLED black |
| Light mode background | Replaced flat `#f5f5f5` with pastel gradient so `backdrop-filter` has colour to blur |
| Chat bubbles | Added CSS variables (`--bubble-ai-bg`, `--bubble-ai-text`) — light grey `#f0f0f0` on dark, matching Agent Dashboard style |
| Input area | Added CSS variables (`--input-area-bg`, `--input-area-border`) for dark mode input/textarea |
| Ticket queue | `TicketCard.jsx` now uses CSS variables for border/bg; non-selected cards inherit theme `colorBgContainer` (same as Admin Dashboard) |
| Stat card titles | `html[data-theme='light']` → black; `html[data-theme='dark']` → near-white via `.ant-statistic-title` CSS override |
| Default buttons | `.ant-btn-default:not(:disabled):not(.ant-btn-dangerous)` → brighter border + white text in dark mode |
| Disabled inputs | `.ant-input[disabled]` → readable but muted style in dark mode |
| Tags | All preset-coloured tags (red/green/blue etc.) → solid saturated bg + white text; default tags → slate grey `#4b5563` + white |
| Danger buttons | "Close Ticket" and "Escalate to Human" → `type="primary" danger` (filled red, not just outlined) |
| Table headers | `.ant-table-thead > tr > th` → `#e8edf5` bg + near-black text (light); `#2d3748` bg + white text (dark); `font-weight: 700` both |
| Alert banners | `.ant-alert-info/success/warning/error` → tinted semi-transparent bg (`rgba(hue, 0.28)`) + matching border (`0.55`) + near-white text in dark mode |

### Step Q — True HITL & UX Improvements (Detail)

| Area | Change | Files |
|------|--------|-------|
| True HITL | Added `generate_suggested_response()` to Orchestrator — calls LLM on ticket creation to produce a real AI draft reply | `src/orchestrator.py` |
| Ticket creation | `create_ticket()` now stores `suggested_response` (LLM draft) and `resolve_action` fields on every ticket | `src/api.py` |
| Approve AI Response | When approved, backend copies `suggested_response` → `agent_reply` and sets `resolve_action: "approved"` | `src/api.py` |
| AI Suggested Response UI | Now shows real LLM draft (green); falls back to honest warning (amber) if AI couldn't generate one | `AgentDashboard.jsx` |
| Approve button disabled | "Approve AI Response" button is greyed out when no AI draft exists (`aiResponse` is null) | `AgentDashboard.jsx` |
| Instant confirmation | After approving, local state updates `agentReplySent` and `resolveAction` immediately — no page reload needed | `AgentDashboard.jsx` |
| Approval label | "AI Response Approved — Sent to Customer" (blue) shown with the AI text after approval; "Custom Reply Sent to Customer" for manual replies | `AgentDashboard.jsx` |
| Escalate button hidden | "Escalate to Human" button is hidden until the customer has sent at least one message (`messages.length > 1`) | `ChatWindow.jsx` |

### Step R — Code Cleanup & Shared Utilities (Detail)

A code quality pass with no user-visible changes. Found and fixed duplicate helper functions and minor Python inefficiencies.

| Area | Change | Files |
|------|--------|-------|
| Shared formatters | Created `ui/src/utils/formatters.js` with `capitalize()`, `formatCategory()`, and `mapSentiment()` — these three functions were each duplicated across 2–3 page/component files | `ui/src/utils/formatters.js` (new) |
| AgentDashboard cleanup | Removed 3 local helper functions (`capitalize`, `formatCategory`, `mapSentiment`); now imports from shared utils | `AgentDashboard.jsx` |
| ChatWindow cleanup | Removed 2 local helper functions (`capitalize`, `formatCategory`); now imports from shared utils | `ChatWindow.jsx` |
| AdminDashboard cleanup | Removed local `formatCategory`; now imports from shared utils (calls `formatCategory(cat, 'Unknown')` to preserve the existing fallback label) | `AdminDashboard.jsx` |
| Python extend | `generate_suggested_response()` — replaced `for msg in history: messages.append(msg)` with idiomatic `messages.extend(conversation_history)` | `src/orchestrator.py` |
| Python redundant `or None` | `ticket.get("suggested_response") or None` → `ticket.get("suggested_response")` — `.get()` already returns `None` by default; the suffix was a no-op | `src/api.py` |

### Step S — Self-Learning Vector DB / Approved Answers (Detail)

Implements a self-improving feedback loop: when a human agent approves or custom-replies to an escalated ticket, the validated Q&A pair is automatically saved to ChromaDB. Future customers asking similar questions will be answered by the AI directly — reducing escalations and closing knowledge gaps over time.

**The feedback loop:**
```
Customer asks question
  → AI can't answer confidently → Escalated
    → Human agent approves answer → Saved to ChromaDB (approved_answers)
      → Next customer asks similar question
        → AI retrieves the approved answer → Resolved without escalation
          → Escalation rate drops → Knowledge Gap Alert disappears
```

| Area | Change | Files |
|------|--------|-------|
| New ChromaDB collection | Added `self.approved_collection` to `VectorDB.__init__` — a second collection (`approved_answers`) separate from the curated `customer_support_kb` | `src/vector_db.py` |
| `add_approved_answer()` | New method on `VectorDB` — stores `"Q: {question}\nA: {answer}"` with metadata `{category, source: "human_approved"}`. Uses `upsert` so storing the same Q&A twice is safe | `src/vector_db.py` |
| Unified `search()` | Updated `VectorDB.search()` to query both `customer_support_kb` and `approved_answers`, merge results, sort by similarity, and return the top-k across both. No change required in `InformationRetrievalAgent` | `src/vector_db.py` |
| Auto-save on resolve | In `resolve_ticket()`, after `agent_reply` is set (for both `approved` and `custom_reply` actions), calls `add_approved_answer()` via `orchestrator.info_agent.vector_db` — reuses the existing DB connection, no new imports | `src/api.py` |

**Design decisions:**
- Stored in a **separate collection** (`approved_answers`) — keeps curated KB clean and auditable; learned content can be inspected or cleared independently
- **Both `approved` and `custom_reply`** trigger a save — `approved` means the AI was correct; `custom_reply` means the human corrected the AI (the most valuable learning signal)
- **`closed` does NOT trigger a save** — no reply was sent, so there's nothing to learn from
- `information_retrieval_agent.py` required **zero changes** — the merge happens transparently inside `VectorDB.search()`

### Step T — XAI Traces, Escalation UX, Date Format & Bug Fixes (Detail)

| Area | Change | Files |
|------|--------|-------|
| **Bug fix: Knowledge Gap Alerts** | `analytics_agent.py` logged `resolution.get('escalated', False)` — but the response dict uses `status: 'escalated'`, not a boolean key, so escalations were never counted. Fixed to `resolution.get('status') == 'escalated'`. Knowledge Gap Alerts now populate correctly. | `src/agents/analytics_agent.py` |
| **XAI richer explanation** | `triage_agent.py` now builds a structured explanation: Category + how determined (keyword/ML/no match), Confidence %, Sentiment, Priority, and Routing decision with reasons (e.g. *"Routed to: Human Agent (negative sentiment, high priority)"*). Previously only showed *"Sentiment detected as neutral"*. | `src/agents/triage_agent.py` |
| **XAI table new columns** | Added Priority (colour-coded tag), Sentiment (colour-coded tag), and Confidence columns to the XAI Decision Traces table. All data was already in the API — just not displayed. | `ui/src/pages/AdminDashboard.jsx` |
| **Escalation message** | Changed from *"Connecting you to a human agent."* (implies real-time handover) to *"Your case has been escalated. Our support team will review it and follow up with you shortly."* — honest about the async nature of the ticket workflow. | `src/orchestrator.py` |
| **Ticket reference in chat** | Customer chat now shows the ticket ID after escalation: *"…Your reference number is TKT-00001."* The same reference is also stored in the conversation history (backend) so the agent sees the same text the customer saw. | `ui/src/components/ChatWindow.jsx`, `src/api.py` |
| **Date/time format** | Added `formatTimestamp()` to shared formatters — outputs `DD MMM YYYY, HH:mm SGT` (e.g. *24 Mar 2026, 14:30 SGT*). Applied consistently in Agent Dashboard and Admin Dashboard. | `ui/src/utils/formatters.js`, `AgentDashboard.jsx`, `AdminDashboard.jsx` |

**Key design note — HITL is async, not real-time:**
When a ticket is escalated, the customer's chat is locked and a ticket is created. The human agent reviews the ticket and approves/replies — but this reply is stored in the ticket, not pushed back to the customer's chat in real time. This is by design for the demo (production would need WebSockets or email). The escalation message was updated to reflect this honestly.

### Step U — Simplify: Code Consolidation & Refactor (Detail)

A second code quality pass. No user-visible behaviour changes.

| Area | Change | Files |
|------|--------|-------|
| **Color constants consolidated** | `PRIORITY_COLORS`, `SENTIMENT_COLORS`, `STATUS_COLORS` were each defined locally in 3–4 files. Moved to `formatters.js` as named exports; all files now import from there | `formatters.js`, `ChatWindow.jsx`, `TicketCard.jsx`, `AgentDashboard.jsx`, `AdminDashboard.jsx` |
| **Single-pass analytics** | `analytics_agent.generate_insights()` made 5 separate passes over `analytics_database`. Replaced with a single loop accumulating all counts simultaneously | `src/agents/analytics_agent.py` |
| **Named thresholds** | Magic numbers replaced with named module-level constants: `ESCALATION_THRESHOLD = 5` (escalation_agent), `ESCALATE_SCORE_THRESHOLD = 5` / `REVISE_SCORE_THRESHOLD = 2` (resolution_agent), `SENTIMENT_POSITIVE_THRESHOLD = 0.2` / `SENTIMENT_NEGATIVE_THRESHOLD = -0.2` (triage_agent) | `src/agents/escalation_agent.py`, `src/agents/resolution_agent.py`, `src/agents/triage_agent.py` |
| **`actionDone` → `actionError`** | `AgentDashboard` had a 4-value string state (`null` / `'approved'` / `'replied'` / `'closed'` / `'error'`) but only the error branch was actually used. Simplified to a boolean `actionError` | `AgentDashboard.jsx` |
| **`runTicketAction` helper** | The three action handlers (`handleApprove`, `handleSendReply`, `handleClose`) each duplicated the same loading/error pattern. Extracted into a single `runTicketAction(fn)` wrapper | `AgentDashboard.jsx` |
| **Timezone consistency** | `analytics_agent.log_interaction()` used `datetime.utcnow()` (timezone-naive) while `api.py` used `datetime.now(timezone.utc)` (timezone-aware). Unified to timezone-aware | `src/agents/analytics_agent.py` |

### Step V — Security: API Key Authentication (Detail)

Added authentication to all internal (agent/admin) endpoints to prevent unauthorised access to ticket data and analytics.

| Area | Change | Files |
|------|--------|-------|
| **`require_internal_key` dependency** | New FastAPI `Depends` function — reads `INTERNAL_API_KEY` from env and validates the `X-API-Key` request header. Returns 401 if missing or wrong | `src/api.py` |
| **5 endpoints protected** | `GET /api/tickets`, `GET /api/tickets/{id}`, `POST /api/tickets/{id}/resolve`, `GET /api/analytics/summary`, `GET /api/analytics/xai-traces` all require the API key. `POST /api/chat` is left unauthenticated (public-facing) | `src/api.py` |
| **Axios instance pre-configured** | `api.js` creates a shared Axios instance with `X-API-Key` header set from `VITE_INTERNAL_API_KEY` env var — all API call functions automatically include it | `ui/src/services/api.js` |
| **`.env` updated** | Added `INTERNAL_API_KEY` to the backend `.env` file (gitignored) | `.env` |
| **`ui/.env.development` created** | New gitignored file with `VITE_API_URL=http://localhost:8000` and `VITE_INTERNAL_API_KEY=<same-value>` for local frontend dev | `ui/.env.development` |

**For production deployment:** Set `INTERNAL_API_KEY` as an environment variable on the backend host (Render/Azure) and `VITE_INTERNAL_API_KEY` in the Vercel dashboard — both must use the same value. See `DEPLOYMENT.md` for full instructions.

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

