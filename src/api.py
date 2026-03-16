"""
API Layer for AI Customer Support System
=========================================
This file wraps the Orchestrator as a FastAPI web server.
The React UI sends HTTP requests here, and this file calls
the Orchestrator which routes to the correct agent.

Run with:
    uvicorn src.api:app --reload --port 8000

Interactive docs available at:
    http://localhost:8000/docs
"""

# =============================================================
# SECTION 1: IMPORTS
# =============================================================

import os
import sys
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# This tells Python to look for other files in the src/ folder.
# Without this, "from orchestrator import Orchestrator" would fail
# when we run from the project root.
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import Orchestrator


# =============================================================
# SECTION 2: APP SETUP
# =============================================================

# Load environment variables from .env file (e.g. OPENAI_API_KEY)
load_dotenv()

# Create the FastAPI application
app = FastAPI(
    title="AI Support System API",
    description="Web API layer connecting the React UI to the multi-agent Orchestrator.",
    version="1.0.0"
)

# Add CORS middleware so the browser (React UI) is allowed to call this server.
# Without this, the browser blocks the request as a security measure.
# Allow-origins lists every URL that is allowed to make requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",       # React UI in local development
        "http://localhost:3000",       # Alternative local dev port
        "https://*.vercel.app",        # Vercel production deployment
        "https://*.azurestaticapps.net"  # Azure Static Web Apps
    ],
    allow_credentials=True,
    allow_methods=["*"],    # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],    # Allow all request headers
)

# Initialise the Orchestrator once when the server starts.
# It loads all 7 agents into memory and is ready to process requests.
# The OpenAI API key is read from the .env file automatically.
orchestrator = Orchestrator(api_key=os.getenv("OPENAI_API_KEY"))


# =============================================================
# SECTION 3: IN-MEMORY STORAGE
# =============================================================

# --- Sessions ---
# Stores the conversation history for each active customer session.
# Key   = session_id (a random string the browser sends with each message)
# Value = list of {"role": "user" or "assistant", "content": "..."}
#
# Example:
#   sessions["session_abc123"] = [
#       {"role": "user",      "content": "My bill is wrong"},
#       {"role": "assistant", "content": "I can help with that..."}
#   ]
sessions: dict = {}

# --- Tickets ---
# Stores escalated tickets that human agents review in the Agent Dashboard.
# Key   = ticket_id (e.g. "TKT-00001")
# Value = ticket data dictionary
#
# Tickets are created automatically when the Orchestrator decides to escalate.
tickets: dict = {}

# Counter used to generate sequential ticket IDs (TKT-00001, TKT-00002, etc.)
ticket_counter: int = 0


# =============================================================
# SECTION 4: REQUEST / RESPONSE MODELS
# =============================================================

# Pydantic models define the exact shape of data expected in request bodies.
# FastAPI uses these to automatically validate incoming requests.
# Think of them as "forms" — if a required field is missing, FastAPI
# returns a clear error message automatically.

class ChatRequest(BaseModel):
    """Shape of data the UI sends when a customer types a message."""
    message: str
    session_id: str = None  # Optional — a new one is created if not provided


class ResolveRequest(BaseModel):
    """Shape of data the UI sends when a human agent acts on a ticket."""
    action: str             # "approved", "custom_reply", or "closed"
    agent_reply: str = ""   # The custom message typed by the human agent (optional)


# =============================================================
# SECTION 5: HELPER FUNCTIONS
# =============================================================

def create_ticket(session_id: str, last_message: str, orchestrator_result: dict) -> str:
    """
    Creates an escalated ticket and saves it to the tickets store.
    Returns the new ticket_id (e.g. "TKT-00001").
    """
    global ticket_counter
    ticket_counter += 1
    ticket_id = f"TKT-{ticket_counter:05d}"  # Zero-padded: TKT-00001, TKT-00002, etc.

    analysis = orchestrator_result.get("analysis", {})
    response = orchestrator_result.get("response", {})

    tickets[ticket_id] = {
        "ticket_id":           ticket_id,
        "session_id":          session_id,
        "status":              "open",
        "queue":               response.get("queue", "general_support"),
        "category":            analysis.get("category", "general_inquiry"),
        "priority":            analysis.get("priority", "low"),
        "sentiment":           analysis.get("sentiment", "neutral"),
        "last_message":        last_message,
        "agent_reply":         None,
        "created_at":          datetime.now(timezone.utc).isoformat(),
        "resolved_at":         None,
        "conversation_history": sessions.get(session_id, []),
        "escalation_reason":   analysis.get("explanation", ""),
    }

    return ticket_id


# =============================================================
# SECTION 6: API ENDPOINTS
# =============================================================

# -------------------------------------------------------
# Health Check
# -------------------------------------------------------

@app.get("/", tags=["System"])
def health_check():
    """
    Health check endpoint.
    Used to verify the server is running.
    Visit http://localhost:8000/ to confirm.
    """
    return {
        "status": "ok",
        "message": "AI Support System API is running",
        "docs": "Visit /docs for the interactive API documentation"
    }


# -------------------------------------------------------
# Endpoint 1: POST /api/chat
# -------------------------------------------------------

@app.post("/api/chat", tags=["Customer Chat"])
def chat(request: ChatRequest):
    """
    Core chat endpoint. Customer sends a message, AI responds.

    Flow:
    1. Look up (or create) conversation history for this session
    2. Pass message + history to the Orchestrator
    3. Orchestrator runs all 7 agents and returns a result
    4. Update session history
    5. If escalated, create a ticket
    6. Return response to browser
    """

    # Use provided session_id, or generate a new one for first-time visitors
    session_id = request.session_id or str(uuid.uuid4())

    # Retrieve the conversation history for this session (empty list if new)
    history = sessions.get(session_id, [])

    # Call the Orchestrator — this runs the full 7-agent pipeline
    result = orchestrator.process_request(request.message, history)

    response = result.get("response", {})
    analysis = result.get("analysis", {})
    status   = response.get("status", "resolved")

    # Update conversation history with the new exchange
    history.append({"role": "user",      "content": request.message})
    if response.get("message"):
        history.append({"role": "assistant", "content": response["message"]})
    sessions[session_id] = history

    # Build the response object to send back to the browser
    api_response = {
        "session_id": session_id,
        "agent":      result.get("agent"),
        "status":     status,
        "message":    response.get("message", ""),
        "analysis": {
            "category":         analysis.get("category"),
            "priority":         analysis.get("priority"),
            "sentiment":        analysis.get("sentiment"),
            "confidence_score": analysis.get("confidence_score"),
            "explanation":      analysis.get("explanation"),
        }
    }

    # If the Orchestrator escalated this request, create a ticket
    if status == "escalated":
        ticket_id = create_ticket(session_id, request.message, result)
        api_response["ticket_id"] = ticket_id
        api_response["queue"]     = response.get("queue")

    return api_response


# -------------------------------------------------------
# Endpoint 2: GET /api/tickets
# -------------------------------------------------------

@app.get("/api/tickets", tags=["Agent Dashboard"])
def get_tickets():
    """
    Returns the list of all escalated tickets.
    Used by the Agent Dashboard to populate the ticket queue.
    """
    # Return tickets as a list, sorted newest first
    ticket_list = list(tickets.values())
    ticket_list.sort(key=lambda t: t["created_at"], reverse=True)
    return ticket_list


# -------------------------------------------------------
# Endpoint 3: GET /api/tickets/{ticket_id}
# -------------------------------------------------------

@app.get("/api/tickets/{ticket_id}", tags=["Agent Dashboard"])
def get_ticket(ticket_id: str):
    """
    Returns a single ticket by its ID.
    Used when the agent clicks on a ticket to see full details.
    """
    ticket = tickets.get(ticket_id)
    if not ticket:
        # 404 = "Not Found" — standard HTTP error code
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found.")
    return ticket


# -------------------------------------------------------
# Endpoint 4: POST /api/tickets/{ticket_id}/resolve
# -------------------------------------------------------

@app.post("/api/tickets/{ticket_id}/resolve", tags=["Agent Dashboard"])
def resolve_ticket(ticket_id: str, request: ResolveRequest):
    """
    Human agent resolves, replies to, or closes a ticket.

    Actions:
    - "approved"     → Accept AI's suggested response, mark resolved
    - "custom_reply" → Agent writes their own reply, mark resolved
    - "closed"       → Close the ticket without a reply
    """
    ticket = tickets.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found.")

    # Map action to a status
    status_map = {
        "approved":     "resolved",
        "custom_reply": "resolved",
        "closed":       "closed",
    }

    ticket["status"]      = status_map.get(request.action, "resolved")
    ticket["agent_reply"] = request.agent_reply or None
    ticket["resolved_at"] = datetime.now(timezone.utc).isoformat()

    return ticket


# -------------------------------------------------------
# Endpoint 5: GET /api/analytics/summary
# -------------------------------------------------------

@app.get("/api/analytics/summary", tags=["Admin Dashboard"])
def analytics_summary():
    """
    Returns system-wide statistics from the Analytics Agent.
    Used by the Admin Dashboard stat cards and charts.
    """
    insights = orchestrator.get_system_insights()
    return insights


# -------------------------------------------------------
# Endpoint 6: GET /api/analytics/xai-traces
# -------------------------------------------------------

@app.get("/api/analytics/xai-traces", tags=["Admin Dashboard"])
def xai_traces():
    """
    Returns the AI decision trace log for all processed requests.
    Each entry shows WHY the AI made a particular routing decision.
    This powers the XAI (Explainable AI) table in the Admin Dashboard.
    """
    traces = []

    for i, entry in enumerate(orchestrator.analytics_db):
        analysis   = entry.get("analysis",   {})
        resolution = entry.get("resolution", {})

        traces.append({
            "trace_id":       f"TRACE-{i + 1:04d}",
            "agent_path":     _build_agent_path(resolution.get("status"), analysis.get("category")),
            "category":       analysis.get("category",  "unknown"),
            "priority":       analysis.get("priority",  "low"),
            "sentiment":      analysis.get("sentiment", "neutral"),
            "decision_reason": analysis.get("explanation", "No explanation recorded"),
            "confidence":     analysis.get("confidence_score", 0.0),
            "status":         resolution.get("status", "unknown"),
            "timestamp":      entry.get("timestamp"),
        })

    # Return most recent first
    traces.reverse()
    return traces


def _build_agent_path(status: str, category: str) -> str:
    """Helper: builds a human-readable agent path string for the XAI table."""
    if status == "blocked":
        return "Security → Blocked"
    if status == "escalated":
        return "Triage → Escalation"
    category_routes = {
        "billing":          "Triage → Resolution",
        "account_issue":    "Triage → Resolution",
        "order_status":     "Triage → Resolution",
        "technical_support":"Triage → IR → Verification → Resolution",
        "general_inquiry":  "Triage → IR → Verification → Resolution",
    }
    return category_routes.get(category, "Triage → Resolution")
