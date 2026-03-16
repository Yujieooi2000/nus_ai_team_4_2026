/**
 * api.js — Centralised API call functions
 * =========================================
 * All HTTP requests to the FastAPI backend live here.
 * Pages/components import these functions instead of calling axios directly.
 *
 * The base URL is read from the environment variable VITE_API_URL:
 *   - Local dev:   http://localhost:8000   (set in ui/.env.development)
 *   - Production:  https://...azurewebsites.net  (set in Vercel dashboard)
 */

import axios from 'axios'

// Base URL from environment variable, with a fallback for safety
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create a reusable axios instance with the base URL pre-configured
const api = axios.create({ baseURL: BASE_URL })


// ─────────────────────────────────────────────────────────────────────────────
// Customer Chat
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Send a customer message to the AI Orchestrator.
 * @param {string} message   - The text the customer typed
 * @param {string} sessionId - Unique ID for this conversation session
 * @returns {object} { session_id, agent, status, message, analysis, ticket_id?, queue? }
 */
export async function sendChatMessage(message, sessionId) {
  const response = await api.post('/api/chat', {
    message,
    session_id: sessionId,
  })
  return response.data
}


// ─────────────────────────────────────────────────────────────────────────────
// Agent Dashboard — Tickets
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Fetch the full list of escalated tickets.
 * @returns {Array} List of ticket objects, newest first
 */
export async function getTickets() {
  const response = await api.get('/api/tickets')
  return response.data
}

/**
 * Fetch a single ticket by its ID.
 * @param {string} ticketId - e.g. "TKT-00001"
 * @returns {object} Single ticket object
 */
export async function getTicket(ticketId) {
  const response = await api.get(`/api/tickets/${ticketId}`)
  return response.data
}

/**
 * Resolve, reply to, or close a ticket.
 * @param {string} ticketId   - e.g. "TKT-00001"
 * @param {string} action     - "approved" | "custom_reply" | "closed"
 * @param {string} agentReply - The human agent's reply text (optional)
 * @returns {object} Updated ticket object
 */
export async function resolveTicket(ticketId, action, agentReply = '') {
  const response = await api.post(`/api/tickets/${ticketId}/resolve`, {
    action,
    agent_reply: agentReply,
  })
  return response.data
}


// ─────────────────────────────────────────────────────────────────────────────
// Admin Dashboard — Analytics
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Fetch system-wide analytics summary from the Analytics Agent.
 * @returns {object} { total_requests, resolved_count, resolution_rate,
 *                     escalation_rate, hallucination_rate,
 *                     avg_retrieval_confidence, category_breakdown }
 */
export async function getAnalyticsSummary() {
  const response = await api.get('/api/analytics/summary')
  return response.data
}

/**
 * Fetch the XAI (Explainable AI) decision trace log.
 * @returns {Array} List of trace objects showing AI reasoning per request
 */
export async function getXaiTraces() {
  const response = await api.get('/api/analytics/xai-traces')
  return response.data
}
