# CI/CD, Containerisation & Cloud Deployment Plan
**Author:** Jonas (UI Lead)
**Date:** 25 Mar 2026
**Last Updated:** 25 Mar 2026
**Status:** Draft — approved approach documented; implementation not yet started

---

## 1. Goal

Define a credible, phased strategy for:
1. Automated testing and deployment (CI/CD) via GitHub Actions
2. Containerising the application with Docker
3. Deploying to cloud (prototype → production path)
4. MLOps — monitoring and maintaining the AI system in production

This document also serves as the basis for presenting the cloud architecture strategy to the professor and assessors.

---

## 2. Current State

| Component | Current Approach | Production Gap |
|---|---|---|
| Backend (FastAPI) | Run locally with `uvicorn` | Not deployed anywhere |
| Frontend (React) | Run locally with `npm run dev` | Not deployed anywhere |
| ChromaDB (vector data) | Local `chroma_data/` folder | Lost on server restart |
| Sessions & tickets | In-memory (Python dicts) | Lost on server restart |
| Tests | `pytest` run manually | Not automated |
| Deployment | Manual (no pipeline) | No CI/CD |

All state resets on server restart. This is intentional for the prototype but must be addressed before production.

---

## 3. Phase 1 — CI with GitHub Actions

**Goal:** Automatically run tests on every push or pull request. Block merges if tests fail.

### How GitHub Actions works

You create YAML files in `.github/workflows/`. GitHub reads these files and runs the steps automatically whenever you push code. No server needed — GitHub provides the compute.

### Workflow 1: Backend CI

Triggered whenever files in `src/` or `tests/` change.

```
Trigger: push or pull_request to main
Steps:
  1. Check out the code
  2. Set up Python 3.11
  3. Install dependencies (pip install -r requirements.txt)
  4. Run pytest tests/
  5. Pass or fail — GitHub shows a green/red badge on the PR
```

**Important consideration — OpenAI API calls in tests:**
Some tests may call the real OpenAI API. Running these on every push would:
- Cost money (charged per API call)
- Make tests slow and dependent on OpenAI uptime

**Recommended solution:** Mock the OpenAI calls in tests using `unittest.mock`. The mock replaces the real API call with a fixed fake response. Tests run instantly, cost nothing, and are not affected by network issues. This is standard practice for AI applications.

### Workflow 2: Frontend CI

Triggered whenever files in `ui/` change.

```
Trigger: push or pull_request to main
Steps:
  1. Check out the code
  2. Set up Node.js 20
  3. Run npm install
  4. Run npm run build
  5. Pass or fail — catches broken imports, missing dependencies, build errors
```

### Files to create

```
.github/
└── workflows/
    ├── backend-ci.yml
    └── frontend-ci.yml
```

---

## 4. Phase 2 — Containerisation with Docker

**Goal:** Package the backend into a Docker container so it runs identically on any machine or cloud platform.

### Why this matters

Without Docker, deploying to a new server means:
- Manually installing Python, pip, dependencies
- Dealing with OS differences
- "It works on my machine" problems

With Docker, you ship the entire runtime environment as one portable unit. The same container runs on your laptop, Render, AWS, or Azure — no changes needed.

### What a Dockerfile does

A `Dockerfile` is a recipe that says: "start from a clean Python environment, copy my code in, install dependencies, and run the server." Docker builds this into an image — a snapshot of the ready-to-run application.

### Files to create

```
Dockerfile          ← backend container definition
.dockerignore       ← tells Docker what to exclude (like node_modules, .env)
docker-compose.yml  ← optional: run frontend + backend together locally
```

### Key design decision: ChromaDB persistence

Currently, ChromaDB writes to `chroma_data/` on the local filesystem. Inside a container, this folder is destroyed every time the container restarts.

**Solution for prototype:** Mount the `chroma_data/` folder as a Docker volume — data persists between restarts on the same machine.

**Solution for production:** Use an external managed vector database (see Phase 3).

---

## 5. Phase 3 — Cloud Deployment Options

### Option A: Render / Railway (Recommended for prototype)

| | Detail |
|---|---|
| **Frontend** | Deploy static build (`npm run build`) directly |
| **Backend** | Deploy Docker container from GitHub repo |
| **Cost** | Free tier available — no credit card risk |
| **CI/CD** | Auto-deploys on every push to `main` — built in |
| **Scaling** | Horizontal scaling available on paid plans |
| **Setup time** | ~2 hours |
| **Containerisation** | Full Docker support |

**Why this is a strong prototype choice:**
- Connects to GitHub — push to main, auto-deploy happens
- Docker containers supported natively
- Free tier has hard limits (no surprise bills)
- The `Dockerfile` written for Render works unchanged on AWS later

**Limitation:** Not suitable for enterprise production (no compliance certifications, limited SLA guarantees).

---

### Option B: AWS (Recommended path for production)

AWS is the right choice once the project moves beyond prototype. The services map cleanly to our stack:

| Component | AWS Service | What it does |
|---|---|---|
| Frontend | S3 + CloudFront | Hosts static files, serves globally via CDN |
| Backend | ECS Fargate | Runs Docker containers, managed by AWS |
| Sessions / tickets | DynamoDB | Managed NoSQL database, replaces in-memory dict |
| Vector DB (ChromaDB) | Amazon OpenSearch or Pinecone | Managed vector search, replaces local ChromaDB |
| Container registry | ECR (Elastic Container Registry) | Stores Docker images, used by ECS |
| Secrets | AWS Secrets Manager | Stores API keys, replaces `.env` file |
| CI/CD | GitHub Actions → ECR → ECS | Build image, push to ECR, deploy to ECS |

**Why AWS is more complex than alternatives:**
AWS gives you full control over networking, security, and scaling — but that control requires configuration (IAM roles, VPCs, security groups, load balancers). A proper AWS setup typically takes a team of engineers 1–2 days minimum.

**Professor's point is valid in context:** AWS is simpler than managing your own bare-metal server. But it is not simpler than Render/Railway for a prototype.

---

### Option C: Azure (Alternative to AWS)

Azure is Microsoft's equivalent to AWS. The services map similarly:

| Component | Azure Service |
|---|---|
| Frontend | Azure Static Web Apps |
| Backend | Azure Container Apps |
| Sessions / tickets | Azure Cosmos DB |
| Vector DB | Azure AI Search |
| Container registry | Azure Container Registry |
| CI/CD | GitHub Actions → ACR → Container Apps |

Azure Static Web Apps has native GitHub Actions integration — similar ease of setup to Render for the frontend. The backend path is similar complexity to AWS.

---

## 6. Architecture Diagrams

### Current State (Prototype, local only)

```
Developer machine
├── npm run dev        → Frontend at localhost:5173
└── uvicorn src.api    → Backend at localhost:8000
                              └── chroma_data/ (local folder)
```

---

### Target: Prototype Cloud Deployment (Render / Railway)

```
GitHub (push to main)
        │
        ├── GitHub Actions ──► Run pytest (backend CI)
        │                  └── Run npm build (frontend CI)
        │
        ├── Render / Railway ──► Frontend (static build)
        │
        └── Render / Railway ──► Backend (Docker container)
                                       └── Mounted volume: chroma_data/
```

---

### Target: Production Cloud Deployment (AWS)

```
GitHub (push to main)
        │
        └── GitHub Actions
                ├── Run tests (pytest + npm build)
                ├── Build Docker image
                ├── Push image to ECR (container registry)
                └── Deploy new image to ECS Fargate
                              │
                     ┌────────┴────────────────────┐
                     │                             │
              Frontend                          Backend
          S3 + CloudFront                    ECS Fargate
         (static React build)           (Docker container)
                                               │
                               ┌───────────────┼───────────────┐
                               │               │               │
                          DynamoDB      Amazon OpenSearch   Secrets Manager
                      (sessions/tickets)  (vector DB /      (API keys)
                                           ChromaDB replacement)
```

**Key architectural insight:** The application code does not change between Render and AWS. Only the infrastructure it runs on changes. The `Dockerfile` is the bridge.

---

## 7. MLOps Considerations

MLOps (Machine Learning Operations) is the practice of maintaining AI systems in production — monitoring their behaviour, detecting drift, and keeping them accurate over time.

### What MLOps means for this system

This system uses OpenAI's API (not a self-trained model), so traditional ML model retraining does not apply. However, several MLOps concerns are still relevant:

### 7.1 Performance Monitoring (already partially built)

The Analytics Agent already tracks these signals in `analytics_db`:

| Metric | What it tells you | Where it's visible |
|---|---|---|
| Resolution rate | % of queries resolved by AI without human help | Admin Dashboard |
| Escalation rate | % escalated to human agents | Admin Dashboard |
| Hallucination rate | % of AI responses flagged by Verification Agent | Admin Dashboard |
| Category breakdown | Which query types are most common | Admin Dashboard (pie chart) |
| Knowledge gaps | Categories with frequent escalations | Admin Dashboard (alerts) |

**Production enhancement:** Persist `analytics_db` to a real database (DynamoDB / CosmosDB) so metrics survive server restarts and can be queried historically.

### 7.2 Prompt Version Management

The system uses prompts embedded in each agent's Python file. In production, prompt changes should be:
- Tracked in version control (already true — they're in code)
- Tested before deployment (CI runs tests on each push)
- Rolled back if they degrade performance (standard Git revert)

**Future enhancement:** Store prompts in a config file or database to allow changes without redeployment.

### 7.3 Self-Learning Vector DB (already built)

The `approved_answers` ChromaDB collection grows automatically as human agents approve ticket replies. This is an MLOps feedback loop:

```
Customer question → AI escalates → Human agent approves reply
       → Q&A saved to approved_answers collection
              → Future similar question → AI resolves directly
                     → Escalation rate drops
```

**Production consideration:** The `approved_answers` collection should be backed up regularly and persisted to a managed vector database (not a local folder).

### 7.4 Drift Detection

Over time, customer query patterns change. A query category that was rare may become common. Signals to watch:

| Signal | Action |
|---|---|
| Knowledge gap alert appears for a new category | Add knowledge base articles for that category |
| Escalation rate rising | Review recent escalated tickets for common themes |
| Hallucination rate rising | Review and tighten agent prompts |
| Resolution rate falling | Check if recent prompt changes degraded quality |

These are already surfaced in the Admin Dashboard. In production, set up alerts (email or Slack) when thresholds are exceeded.

### 7.5 Cost Monitoring

Every customer message triggers OpenAI API calls. In production:
- Monitor token usage per request
- Set spend alerts in OpenAI dashboard
- Consider caching common responses to reduce API calls

---

## 8. Recommended Phased Implementation

| Phase | What | When | Effort |
|---|---|---|---|
| **Phase 1** | GitHub Actions CI (backend pytest + frontend build) | Before submission | Low (~2–4 hours) |
| **Phase 2** | Write `Dockerfile` for backend | Before submission | Low (~2 hours) |
| **Phase 3** | Deploy to Render or Railway via Docker | Before submission | Low (~2 hours) |
| **Phase 4** | Present AWS/Azure target architecture to professor | Before submission | Zero extra effort — use this doc |
| **Phase 5** | Migrate to AWS/Azure if project continues | Post-submission | High (~1–2 days) |

---

## 9. What to Present to the Professor

The key message is: **our application is cloud-ready by design, and we have a clear migration path to AWS/Azure.**

**Points to make:**

1. **Containerised:** The backend runs in a Docker container. The same container image works on Render today and AWS ECS tomorrow — no code changes needed.

2. **CI/CD pipeline:** GitHub Actions runs tests automatically on every push. Deployment to cloud triggers automatically on merge to main.

3. **Known architectural gaps and solutions:** We have two stateful components (ChromaDB and in-memory sessions/tickets) that need to be externalised for production. The solutions are well-understood: managed vector DB and managed NoSQL database respectively.

4. **Why not AWS for the prototype:** We prioritised validating the AI pipeline over cloud infrastructure. Deploying to Render first lets us prove the system works end-to-end with lower setup risk. The architecture is designed to migrate to AWS with minimal rework.

5. **MLOps:** The Analytics Agent already tracks the key production health signals (resolution rate, escalation rate, hallucination rate, knowledge gaps). These would be persisted to a managed database in production and trigger automated alerts.

---

## 10. Known Tradeoffs and Follow-ups

| Decision | Tradeoff | Follow-up |
|---|---|---|
| Render/Railway over AWS for prototype | Faster setup, lower risk, no billing surprise — but not enterprise-grade | Migrate to AWS/Azure if project continues post-submission |
| ChromaDB local volume in Docker | Persists between restarts on same machine — but not if container is moved | Replace with managed vector DB (Pinecone, OpenSearch, Azure AI Search) in production |
| In-memory sessions and tickets | Zero setup — but lost on restart | Replace with DynamoDB or CosmosDB in production |
| Mock OpenAI in CI tests | Tests run fast and free — but don't test real model behaviour | Add separate integration test suite that hits real API, run manually or on schedule |
| Prompts embedded in code | Easy to version control — but requires redeployment to change prompts | Move to config file or prompt management service if iteration speed becomes an issue |
