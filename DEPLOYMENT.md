# Deployment Guide — Taking the System Live

**Project:** AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI / Frontend Lead)
**Last updated:** March 2026
**Purpose:** Step-by-step guide for deploying both the frontend (React) and backend (Python/FastAPI) to the cloud so anyone can access the system via a public URL.

---

## Table of Contents

1. [What Needs to Be Deployed](#1-what-needs-to-be-deployed)
2. [Understanding the ChromaDB Cloud Challenge](#2-understanding-the-chromadb-cloud-challenge)
3. [Recommended Option: Free Hosting (Render + Vercel)](#3-recommended-option-free-hosting-render--vercel)
4. [Alternative Option: Azure (Course/Enterprise Aligned)](#4-alternative-option-azure-courseenterprise-aligned)
5. [Jonas's Tasks: Deploying the Frontend to Vercel](#5-jonass-tasks-deploying-the-frontend-to-vercel)
6. [Teammate Tasks: Deploying the Backend](#6-teammate-tasks-deploying-the-backend)
7. [Connecting Frontend to the Deployed Backend](#7-connecting-frontend-to-the-deployed-backend)
8. [Post-Deployment Checklist](#8-post-deployment-checklist)
9. [Troubleshooting Common Deployment Issues](#9-troubleshooting-common-deployment-issues)
10. [Cost Summary](#10-cost-summary)

---

## 1. What Needs to Be Deployed

The system has two parts that need to go live independently:

```
Your Computer (local)          →    Cloud (accessible by anyone)
─────────────────────────────────────────────────────────────────
React UI (localhost:5173)      →    Frontend hosting (Vercel / Azure Static Web Apps)
FastAPI backend (localhost:8000) →  Backend hosting (Render.com / Azure App Service)
chroma_data/ (local folder)    →    Needs special handling — see Section 2
```

Think of it like opening a restaurant:
- The **frontend** is the dining room — what customers see when they walk in
- The **backend** is the kitchen — where the real work happens
- Both must be open at the same time, and the dining room needs to know the kitchen's address

---

## 2. Understanding the ChromaDB Cloud Challenge

### The Problem

Locally, ChromaDB saves its data into a folder called `chroma_data/` on your computer. Cloud servers work differently — they often don't have permanent storage, or they reset when the server restarts.

This means if you just deploy the backend code without handling ChromaDB, the vector database starts empty every time the server restarts.

### Three Solutions (pick one with your teammate)

| Solution | Difficulty | Cost | Best For |
|----------|-----------|------|---------|
| **A — Bundle data into deployment** | Easy | Free | Prototype / demo |
| **B — Initialise on server startup** | Medium | Free | Prototype / demo |
| **C — Cloud vector database (Pinecone)** | Hard | Free tier available | Production |

---

### Solution A — Bundle `chroma_data/` into the deployment (Recommended for prototype)

**What it means:** Before deploying, run `python src/vector_db.py` locally to generate the `chroma_data/` folder, then temporarily remove `chroma_data/` from `.gitignore`, commit it, deploy, then add it back to `.gitignore`.

**Pros:** Simple, no extra services, works immediately.
**Cons:** The knowledge base is static — to add new documents you must redeploy. Fine for a course demo.

**Steps (teammate does this on backend):**
```bash
# 1. Run init locally to populate chroma_data/
python src/vector_db.py

# 2. Temporarily allow chroma_data/ to be committed
# Edit .gitignore: comment out the chroma_data/ line

# 3. Commit the data
git add chroma_data/
git commit -m "Include vector DB data for deployment"

# 4. Deploy to cloud (see Section 6)

# 5. Restore .gitignore (put chroma_data/ back in)
git checkout .gitignore
```

---

### Solution B — Initialise on server startup (Alternative)

**What it means:** Add code to `src/api.py` that runs `initialize_sample_database()` automatically when the server first starts, if the collection is empty.

**Teammate adds this near the top of `src/api.py`:**
```python
from vector_db import VectorDB, initialize_sample_database

# Initialize vector DB on startup if empty
_vdb = VectorDB()
if _vdb.get_collection_stats()["total_documents"] == 0:
    initialize_sample_database()
```

**Pros:** Fully automatic, no manual steps.
**Cons:** Adds a few seconds to server startup time. The data folder still won't persist after a server restart on some platforms (Render free tier, for example).

---

### Solution C — Use a Cloud Vector Database (Production-grade)

Replace ChromaDB local storage with a managed cloud service like **Pinecone** (free tier available). This is more complex and is a backend task — out of scope for Jonas. Raise this with your teammate if you plan to deploy for real users beyond the course.

---

## 3. Recommended Option: Free Hosting (Render + Vercel)

This is the fastest and cheapest way to get a live demo URL. Both platforms have generous free tiers and deploy directly from GitHub.

```
GitHub Repository
      │
      ├─► Vercel (Frontend)     → https://ai-support.vercel.app
      │        ↑ React UI
      │
      └─► Render.com (Backend)  → https://ai-support-api.onrender.com
               ↑ FastAPI + ChromaDB
```

### Why Render for backend?
- Free tier available (750 hours/month — enough for a demo)
- Supports Python natively — no Docker knowledge needed
- Simple GitHub-connected deployment
- Persistent disk available (paid) — or use Solution A/B above for free

### Why Vercel for frontend?
- The easiest React deployment platform that exists
- Automatically deploys every time you push to GitHub
- Free, no credit card needed
- 100GB bandwidth per month on free tier

> **Limitation of free tiers:** Render's free tier "spins down" the backend server after 15 minutes of inactivity. The first request after spin-down takes ~30 seconds to respond. For a demo this is fine — for real users it's not. Upgrade to a paid plan ($7/month) to avoid this.

---

## 4. Alternative Option: Azure (Course/Enterprise Aligned)

If your course requires Azure or you want NCS-aligned infrastructure:

```
GitHub Repository
      │
      ├─► Azure Static Web Apps (Frontend)   → https://ai-support.azurestaticapps.net
      │
      └─► Azure App Service (Backend)        → https://ai-support-api.azurewebsites.net
               ↑ FastAPI + ChromaDB
```

| Component | Azure Service | Free Tier? | Notes |
|-----------|--------------|-----------|-------|
| Frontend | Azure Static Web Apps | Yes (free) | Great React support |
| Backend | Azure App Service | F1 free tier (limited) | B1 tier ~$13/month for reliable performance |
| Vector DB storage | App Service persistent storage | Included | Use Solution A or B above |

**Azure Advantage:** More professional, NCS-familiar, better for final submission presentation.
**Azure Disadvantage:** More complex to set up, requires an Azure account.

---

## 5. Jonas's Tasks: Deploying the Frontend to Vercel

This is the part Jonas handles. It takes about 10–15 minutes once the teammate has the backend URL ready.

### Prerequisites
- Your code is pushed to GitHub (always keep it up to date)
- Your teammate has given you the live backend URL (e.g., `https://ai-support-api.onrender.com`)

---

### Step 1 — Create a Vercel account

1. Go to **vercel.com**
2. Click **Sign Up**
3. Choose **Continue with GitHub** (this links Vercel to your GitHub account)

---

### Step 2 — Import your project

1. In the Vercel dashboard, click **Add New → Project**
2. Find your `nus_ai_team_4_2026` repository and click **Import**
3. On the configuration screen:
   - **Root Directory:** Click "Edit" and type `ui` — this tells Vercel that the React app lives inside the `ui/` folder, not the project root
   - **Framework Preset:** Should auto-detect as **Vite**
   - **Build Command:** `npm run build` (already set by default)
   - **Output Directory:** `dist` (already set by default)

---

### Step 3 — Set the environment variables

Before clicking Deploy, you must tell the frontend where the backend lives and provide the shared API key:

1. Scroll down to **Environment Variables**
2. Add both of the following:
   - **Name:** `VITE_API_URL` — **Value:** `https://ai-support-api.onrender.com` ← (use your teammate's actual URL here)
   - **Name:** `VITE_INTERNAL_API_KEY` — **Value:** the same secret value as `INTERNAL_API_KEY` set on the backend
3. Make sure the environment is set to **Production**

> **Why this is important:** `VITE_API_URL` tells the React app which backend to call (instead of `localhost:8000`). `VITE_INTERNAL_API_KEY` is required to authenticate against the agent and admin API endpoints — without it, all ticket and analytics requests will return 401.

---

### Step 4 — Deploy

Click **Deploy**. Vercel will:
1. Pull your code from GitHub
2. Run `npm run build` to compile the React app
3. Publish the compiled files to their global CDN
4. Give you a URL like `https://nus-ai-team-4-2026.vercel.app`

The whole process takes 1–2 minutes.

---

### Step 5 — Verify it works

1. Open the Vercel URL in your browser
2. The Customer Chat page should load
3. Type a test message — if the AI responds, the connection to the backend is working
4. If you see a red error banner, check Section 9 (Troubleshooting)

---

### Step 6 — Auto-deployment is now active

From this point on, every time you run `git push` to your main branch, Vercel automatically re-deploys the frontend within 1–2 minutes. You never need to manually re-deploy unless you change environment variables.

---

### Deploying to Azure Static Web Apps (Alternative to Vercel)

If you need Azure instead:

1. Go to **portal.azure.com** → Create a resource → **Static Web App**
2. Connect it to your GitHub repository
3. Set the **App location** to `/ui` and **Output location** to `dist`
4. Add the `VITE_API_URL` environment variable in **Configuration → Application settings**
5. Azure will auto-deploy from GitHub just like Vercel

---

## 6. Teammate Tasks: Deploying the Backend

This section is for reference — it is the backend teammate's responsibility, not Jonas's. Share this with them.

### Deploying to Render.com (Free option)

1. Go to **render.com** and sign up with GitHub
2. Click **New → Web Service**
3. Connect your `nus_ai_team_4_2026` repository
4. Configure:
   - **Root Directory:** (leave blank — Render needs the full repo)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python -m textblob.download_corpora && python src/vector_db.py`
   - **Start Command:** `python -m uvicorn src.api:app --host 0.0.0.0 --port 8000`
5. Add environment variables:
   - `OPENAI_API_KEY` = your OpenAI key
   - `INTERNAL_API_KEY` = a random secret string (must match `VITE_INTERNAL_API_KEY` set in Vercel)
6. Click **Create Web Service**

> The Build Command above runs `python src/vector_db.py` during deployment — this is Solution B (initialise on build). The `chroma_data/` folder will not persist between deploys, so each new deploy re-initialises the knowledge base.

### Deploying to Azure App Service

1. Install Azure CLI: `winget install Microsoft.AzureCLI`
2. Log in: `az login`
3. Deploy from the project root:
```bash
az webapp up \
  --name ai-support-api \
  --runtime "PYTHON:3.11" \
  --sku B1
```
4. Set the API keys:
```bash
az webapp config appsettings set \
  --name ai-support-api \
  --settings OPENAI_API_KEY="sk-..." INTERNAL_API_KEY="your-secret-key-here"
```
5. Note the URL: `https://ai-support-api.azurewebsites.net`

### Important: Update CORS for Production

After deploying the backend, the teammate must update the CORS settings in `src/api.py` to include the live frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",           # ← add the Vercel URL
        "https://your-app.azurestaticapps.net",  # ← or Azure URL
    ],
    ...
)
```

Without this, the browser will block all API calls from the live frontend.

---

## 7. Connecting Frontend to the Deployed Backend

Once both are deployed, the only connection between them is the `VITE_API_URL` environment variable you set in Step 3 above. If you need to change the backend URL later:

1. Go to **Vercel Dashboard → Your Project → Settings → Environment Variables**
2. Edit `VITE_API_URL` with the new backend URL
3. Go to **Deployments** and click **Redeploy** on the latest deployment

That's it — no code changes needed.

---

## 8. Post-Deployment Checklist

After both frontend and backend are deployed, verify each item:

### Connectivity
- [ ] Frontend URL loads without errors in the browser
- [ ] Customer Chat: send a test message — AI responds correctly
- [ ] Agent Dashboard: send an escalation trigger, ticket appears in the queue
- [ ] Admin Dashboard: stat cards show real numbers (not zero)

### Security
- [ ] `OPENAI_API_KEY` is set only in the cloud platform's environment settings — never in code
- [ ] `INTERNAL_API_KEY` is set on the backend host and `VITE_INTERNAL_API_KEY` is set in Vercel — same value, never committed to git
- [ ] `.env` and `ui/.env.development` are not committed to GitHub (check with `git log --all -- .env`)
- [ ] Backend CORS only allows your frontend's URL — not all origins (`*`)
- [ ] The backend API URL in Vercel uses `https://` not `http://`

### Vector Database
- [ ] Customer Chat gives relevant answers (not generic "I don't know" responses)
- [ ] If answers seem poor, ask teammate to check if ChromaDB initialised correctly on the server

---

## 9. Troubleshooting Common Deployment Issues

| Problem | What It Means | Fix |
|---------|--------------|-----|
| Frontend loads but chat gives a red error | Frontend cannot reach the backend | Check `VITE_API_URL` is correct in Vercel environment variables |
| Backend URL returns 404 | Wrong URL or backend not deployed | Confirm the backend URL from Render/Azure — test it directly in your browser at `/docs` |
| First chat message takes 30+ seconds | Render free tier is spinning up | Normal — wait for first response, subsequent ones are fast. Or upgrade to paid |
| "CORS error" in browser console (F12) | Backend CORS does not include the frontend URL | Ask teammate to add your Vercel URL to the `allow_origins` list in `src/api.py` |
| AI gives very generic or irrelevant answers | ChromaDB not initialised on the server | Ask teammate to re-run the build or add the init step to the server startup |
| Vercel build fails | `npm run build` error | Check the Vercel build log — usually a missing package or env variable |
| Azure deployment hangs | Azure CLI timeout | Try `az webapp restart --name ai-support-api` |
| Tickets disappear after some time | In-memory ticket storage resets on server restart | Expected for prototype — not a bug. Production would use a real database |

---

## 10. Cost Summary

### Free Path (Recommended for prototype/demo)

| Service | Cost | Limit |
|---------|------|-------|
| Vercel (frontend) | **Free** | 100GB bandwidth, unlimited deploys |
| Render.com (backend) | **Free** | 750 hours/month, spins down after 15 min idle |
| OpenAI API | Pay-per-use | ~$0.01–0.05 per conversation (GPT-4o-mini) |
| ChromaDB | **Free** | Local storage on the server |
| **Total** | **~$0–$5/month** depending on OpenAI usage | |

### Azure Path (Course/enterprise)

| Service | Cost |
|---------|------|
| Azure Static Web Apps (frontend) | **Free** |
| Azure App Service B1 (backend) | ~$13/month |
| OpenAI API | Pay-per-use |
| **Total** | **~$13–20/month** |

> **Tip:** For the course demo, use the free path. Only move to Azure if required for the final submission or if you need the Azure branding for presentation purposes.

---

*This guide covers everything needed to take the project from local development to a live, publicly accessible URL. Once deployed, share the frontend URL with your course assessors and teammates.*
