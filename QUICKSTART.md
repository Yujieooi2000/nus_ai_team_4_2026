# Quick-Start Guide — Running the Project Locally

**Project:** AI-Powered Customer Support Triage and Resolution System
**Last updated:** March 2026

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key

---

## Step 1 — Clone and set up Python

```bash
git clone <repo-url>
cd nus_ai_team_4_2026

pip install -r requirements.txt
python -m textblob.download_corpora
```

---

## Step 2 — Initialise the Vector Database (one-time setup)

The AI uses ChromaDB to search the knowledge base semantically (by meaning, not just keywords). You need to load the knowledge base into it once before starting the server.

```bash
python src/vector_db.py
```

You should see:
```
✓ Vector DB initialized at ./chroma_data
✓ Successfully added 15 documents to vector database
✓ VECTOR DATABASE INITIALIZATION COMPLETE
```

> **Only do this once.** The data is saved in the `chroma_data/` folder and survives server restarts. If you see `⚠ Vector DB initialization failed` in the terminal later, just re-run this step.

---

## Step 3 — Set your API keys

Create a file called **`.env`** in the project root (this file is git-ignored and must not be committed):

```
OPENAI_API_KEY=sk-...your-key-here...
INTERNAL_API_KEY=your-secret-key-here
```

`INTERNAL_API_KEY` protects the agent and admin endpoints (tickets, analytics) from unauthenticated access. You can use any random string — just make sure it matches the value in `ui/.env.development` (see Step 5).

Also create **`ui/.env.development`** inside the `ui/` folder (also git-ignored):

```
VITE_API_URL=http://localhost:8000
VITE_INTERNAL_API_KEY=your-secret-key-here
```

Use the **same value** for `INTERNAL_API_KEY` and `VITE_INTERNAL_API_KEY`.

---

## Step 4 — Start the backend API server

Run this from the project root:

```bash
python -m uvicorn src.api:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Verify it works by opening **http://localhost:8000/docs** in your browser — you should see 6 endpoints listed.

---

## Step 5 — Start the React frontend

Open a **second terminal**, then:

```bash
cd ui
npm install
npm run dev
```

You should see:

```
VITE ready on http://localhost:5173
```

Open **http://localhost:5173** in your browser.

> **Both terminals must stay open while testing** — one for the backend, one for the frontend.

---

## Step 6 — Test the full flow

1. **Customer Chat** — type a message and verify the AI responds. Send something frustrated or urgent (e.g. *"I am very frustrated, I want a refund NOW"*) to trigger an escalation.
2. **Agent Dashboard** — the escalated ticket should appear in the queue. Click it to review the conversation, then try Approve / Custom Reply / Close.
3. **Admin Dashboard** — verify the stat cards and XAI Traces table show real data.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uvicorn` not recognized as a command | Use `python -m uvicorn ...` instead of just `uvicorn` |
| `ModuleNotFoundError: textblob` | Run `pip install textblob` then `python -m textblob.download_corpora` |
| Any dashboard shows a red error banner | Make sure the backend server is running on port 8000 before opening the UI |
| No tickets appearing in Agent Dashboard | Send a message that triggers escalation (see Step 5 example above) |
| `SyntaxError` in `security_compliance_agent.py` | This is a pre-existing bug — it has already been fixed in the current codebase |
