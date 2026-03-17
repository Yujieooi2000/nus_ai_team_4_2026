# Design Decisions & Known Behaviours

**Project:** AI-Powered Customer Support Triage and Resolution System
**Author:** Jonas (UI / Frontend Lead)
**Date:** March 2026
**Purpose:** Documents intentional design choices made during integration. Read this before making enhancements to the UI so you understand *why* things work the way they do.

---

## 1. Ticket Workflow — Why the Agent's Reply Does Not Appear in Customer Chat

### Behaviour
When a human agent writes a custom reply in the Agent Dashboard, the customer does not see it in their chat window. The customer chat shows an escalation message and locks.

### Designed Flow

```
Customer chats in Customer Chat Portal
        ↓
AI Orchestrator cannot resolve → escalates
        ↓
Chat locks ("You will be contacted shortly")
        ↓
Human agent reads conversation in Agent Dashboard
        ↓
Human agent sends reply → ticket marked Resolved
        ↓
Customer starts a new chat if they have further questions
```

### Why There Is No "Continue in the Same Chat Window"

That would require a **live two-way connection (WebSockets)** — a persistent open connection between the customer's browser and the agent's browser that pushes messages in real time. This is far beyond prototype scope.

The human agent's reply is the **final answer on that ticket**. If the customer has more to say, they start a fresh chat. This is exactly how email ticketing systems like **Zendesk** and **Freshdesk** work.

### Future Enhancement
Implement WebSocket support (e.g., FastAPI native WebSocket endpoint + a `useEffect` listener in React) to push the agent's reply into the customer chat in real time.

---

## 2. Customer Chat Reset — Why the Chat Clears on Navigate Away

### Behaviour
When the customer navigates away from the Customer Chat page and returns (or refreshes), the entire conversation history disappears and a fresh chat starts.

### Why This Happens
The `messages` array and `sessionId` live in **React component state and `useRef`** — in-memory only, inside the browser's RAM for the current page visit. When the component is destroyed (navigate away / refresh), React creates it fresh:
- A new `sessionId` is generated
- The `messages` array resets to just the welcome message
- Previous conversation history is gone from the UI

### Why This Is Intentional (for Prototype)
The agent's reply is stored in the ticket in the Agent Dashboard — the conversation record is preserved there. For the course submission, chat persistence across navigation is not required. Implementing it would add complexity without benefit to the demo.

### Future Enhancement (Simple)
Store `sessionId` in `sessionStorage` on mount and restore `messages` from it. This would survive page refreshes within the same browser tab:

```javascript
// On mount: restore session
const savedId   = sessionStorage.getItem('sessionId')
const sessionId = useRef(savedId || `session_${Date.now()}_${Math.random().toString(36).slice(2)}`)
sessionStorage.setItem('sessionId', sessionId.current)

// On new message: persist messages
sessionStorage.setItem('messages', JSON.stringify(messages))

// On mount: restore messages
const savedMessages = sessionStorage.getItem('messages')
const [messages, setMessages] = useState(savedMessages ? JSON.parse(savedMessages) : [welcomeMsg])
```

---

## 3. True Human-in-the-Loop (HITL) — How AI Suggested Response Works

### Behaviour
The Agent Dashboard ticket detail panel implements genuine HITL:
- **"AI Suggested Response"** (green) — a real LLM-generated draft reply, created automatically when the ticket is escalated
- **"AI Response Approved — Sent to Customer"** (blue) — appears after the agent clicks "Approve AI Response", showing the approved AI text
- **"Custom Reply Sent to Customer"** (blue) — appears after the agent writes and sends their own reply

### How the Draft Is Generated
When `create_ticket()` runs in `src/api.py`, it immediately calls `orchestrator.generate_suggested_response(conversation_history)`. This sends the full conversation history to the LLM with a system prompt asking it to draft a concise, empathetic, customer-facing reply for the human agent to review. The draft is stored as `suggested_response` on the ticket.

If the LLM call fails (API error, empty history, etc.), `suggested_response` is `None` and the UI shows a warning in place of the green box explaining that no draft is available.

### Why Two Separate Boxes Are Kept
The agent's reply (whether approved AI draft or custom text) is stored in a separate field (`agentReplySent`) and rendered in its own labelled box. The `aiResponse` field (the original AI draft) is never overwritten — even after approval.

This preserves a clear **audit trail**: anyone reviewing the ticket can always see both what the AI originally suggested and what was ultimately sent to the customer.

### Approve AI Response Flow
Clicking "Approve AI Response":
1. Calls `POST /api/tickets/{id}/resolve` with `action: "approved"`
2. Backend copies `suggested_response` → `agent_reply` and sets `resolve_action: "approved"`
3. Frontend immediately updates local state with `agentReplySent` and `resolveAction`
4. The "AI Response Approved — Sent to Customer" confirmation box appears instantly

### "Approve AI Response" Button Disabled When No Draft
If `suggested_response` is `None` (AI couldn't generate a draft), the "Approve AI Response" button is greyed out with a tooltip explaining why. The agent must write a custom reply instead.

---

## 4. Action Buttons Disappear After Resolution — Why This Is Correct

### Behaviour
Once a ticket is Resolved or Closed, the "Approve AI Response", "Write Custom Reply", and "Close Ticket" buttons disappear and do not come back, even if you click away to another ticket and return.

### Why
The buttons are gated on `selected.status === 'Open'` — this reads from the ticket's `status` field stored in the tickets array in React state, which persists across ticket switches. A resolved ticket keeps `status: 'Resolved'` no matter how many times you select it.

An earlier version gated on `!actionDone` — this was reset to `null` every time you clicked a different ticket, causing the buttons to reappear after switching. That was a bug; the current approach is correct.

---

*Last updated: March 2026*
