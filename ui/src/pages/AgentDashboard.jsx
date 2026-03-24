import { useState, useEffect } from 'react'
import { Typography, Tag, Button, Input, Alert, Empty, Space, Divider, Card, Spin } from 'antd'
import TicketCard from '../components/TicketCard'
import { getTickets, resolveTicket } from '../services/api'
import { capitalize, formatCategory, mapSentiment } from '../utils/formatters'

const { Title, Text } = Typography
const { TextArea } = Input

// ── Colour maps ────────────────────────────────────────────────────────────────
const PRIORITY_COLORS  = { High: 'red', Medium: 'orange', Low: 'green' }
const SENTIMENT_COLORS = { Frustrated: 'volcano', Neutral: 'default', Satisfied: 'green' }

// ── Helper: map API ticket format to the shape the UI components expect ────────
// The API returns field names like ticket_id, conversation_history, etc.
// This function converts them to the names used by TicketCard and the detail panel.
function mapTicket(t) {
  return {
    id:        t.ticket_id,
    // The API doesn't store a customer name — show a short session reference instead
    customer:  `Session ${String(t.session_id || '').slice(-8)}`,
    priority:  capitalize(t.priority),
    // Map API sentiment ("negative"/"neutral"/"positive") to display labels
    sentiment: mapSentiment(t.sentiment),
    category:  formatCategory(t.category),
    timestamp: t.created_at
      ? new Date(t.created_at).toLocaleString('en-SG', { dateStyle: 'short', timeStyle: 'short', timeZone: 'Asia/Singapore' })
      : '',
    status:    capitalize(t.status),
    preview:   t.last_message || '',
    // AI summary uses the triage explanation (the XAI trace for this ticket)
    aiSummary: t.escalation_reason
      ? `Escalation reason: ${t.escalation_reason}`
      : 'Escalated for human review.',
    // AI suggested response — LLM-generated draft for the human agent to review (HITL).
    // null means the AI could not generate a draft for this ticket.
    aiResponse: t.suggested_response || null,
    // If the ticket was already resolved, restore the reply and action from the API
    agentReplySent: t.agent_reply || null,
    resolveAction:  t.resolve_action || null,
    // Map conversation history: API uses "assistant", UI uses "ai"
    conversation: (t.conversation_history || []).map(m => ({
      role: m.role === 'assistant' ? 'ai' : m.role,
      text: m.content || '',
    })),
    // Keep the original ticket_id for API calls
    _ticketId: t.ticket_id,
  }
}

// ── Helper: read-only conversation bubbles (same style as CustomerChat) ────────
function ConversationHistory({ conversation }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {conversation.map((msg, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}
        >
          <div style={{
            maxWidth: '72%',
            padding: '9px 13px',
            borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            background: msg.role === 'user' ? '#1677ff' : '#f0f0f0',
            color: msg.role === 'user' ? 'white' : '#222',
            fontSize: 13,
          }}>
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  )
}


// ── Main page component ────────────────────────────────────────────────────────
function AgentDashboard() {
  const [tickets, setTickets]             = useState([])
  const [loading, setLoading]             = useState(true)
  const [error, setError]                 = useState(null)
  const [selectedId, setSelectedId]       = useState(null)
  const [showReplyBox, setShowReplyBox]   = useState(false)
  const [customReply, setCustomReply]     = useState('')
  const [actionDone, setActionDone]       = useState(null) // 'approved' | 'replied' | 'closed'
  const [actionLoading, setActionLoading] = useState(false)

  // Load tickets from the API when the page first loads
  useEffect(() => {
    async function fetchTickets() {
      try {
        const data = await getTickets()
        setTickets(data.map(mapTicket))
      } catch (err) {
        setError('Could not load tickets. Is the API server running?')
      } finally {
        setLoading(false)
      }
    }
    fetchTickets()
  }, [])

  const selected = tickets.find(t => t.id === selectedId)

  // Update one or more fields on a ticket in local state after an action
  function updateLocalTicket(id, updates) {
    setTickets(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t))
  }

  function handleSelectTicket(id) {
    setSelectedId(id)
    setShowReplyBox(false)
    setCustomReply('')
    setActionDone(null)
  }

  async function handleApprove() {
    setActionLoading(true)
    try {
      await resolveTicket(selected._ticketId, 'approved')
      updateLocalTicket(selectedId, {
        status: 'Resolved',
        agentReplySent: selected.aiResponse,
        resolveAction: 'approved',
      })
      setActionDone('approved')
    } catch (err) {
      setActionDone('error')
    } finally {
      setActionLoading(false)
    }
  }

  async function handleSendReply() {
    if (!customReply.trim()) return
    setActionLoading(true)
    try {
      await resolveTicket(selected._ticketId, 'custom_reply', customReply)
      // Store the agent's reply in a separate field — aiResponse stays as the AI draft
      updateLocalTicket(selectedId, { status: 'Resolved', agentReplySent: customReply })
      setActionDone('replied')
      setShowReplyBox(false)
    } catch (err) {
      setActionDone('error')
    } finally {
      setActionLoading(false)
    }
  }

  async function handleClose() {
    setActionLoading(true)
    try {
      await resolveTicket(selected._ticketId, 'closed')
      updateLocalTicket(selectedId, { status: 'Closed' })
      setActionDone('closed')
    } catch (err) {
      setActionDone('error')
    } finally {
      setActionLoading(false)
    }
  }

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ height: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip="Loading tickets..." />
      </div>
    )
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <Alert
        type="error"
        message="Could not load tickets"
        description={error}
        showIcon
        style={{ margin: '40px auto', maxWidth: 600 }}
      />
    )
  }

  return (
    <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 112px)' }}>

      {/* ── LEFT PANEL: Ticket queue ──────────────────────────────── */}
      <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
        <Title level={4} style={{ marginBottom: 12 }}>
          Ticket Queue
          <Tag color="blue" style={{ marginLeft: 8, fontWeight: 'normal' }}>
            {tickets.filter(t => t.status === 'Open').length} Open
          </Tag>
        </Title>
        <div style={{ overflowY: 'auto', flex: 1 }}>
          {tickets.length === 0 ? (
            <Empty description="No escalated tickets yet" style={{ marginTop: 40 }} />
          ) : (
            tickets.map(ticket => (
              <TicketCard
                key={ticket.id}
                ticket={ticket}
                selected={ticket.id === selectedId}
                onClick={() => handleSelectTicket(ticket.id)}
              />
            ))
          )}
        </div>
      </div>

      {/* ── RIGHT PANEL: Ticket detail ────────────────────────────── */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {!selected ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Empty description="Select a ticket from the queue to view details" />
          </div>
        ) : (
          <Card style={{ borderRadius: 10 }}>

            {/* Ticket header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div>
                <Title level={4} style={{ margin: 0 }}>{selected.id}</Title>
                <Text type="secondary">{selected.customer} · {selected.timestamp}</Text>
              </div>
              <Space>
                <Tag color={PRIORITY_COLORS[selected.priority]}>{selected.priority} Priority</Tag>
                <Tag color={SENTIMENT_COLORS[selected.sentiment]}>{selected.sentiment}</Tag>
                <Tag>{selected.category}</Tag>
              </Space>
            </div>

            <Divider style={{ margin: '12px 0' }} />

            {/* Conversation history */}
            <Text strong style={{ display: 'block', marginBottom: 10 }}>Conversation History</Text>
            {selected.conversation.length > 0
              ? <ConversationHistory conversation={selected.conversation} />
              : <Text type="secondary">No conversation history recorded.</Text>
            }

            <Divider style={{ margin: '16px 0' }} />

            {/* AI Summary (escalation reason from triage) */}
            <Alert
              message={<Text strong>AI Summary</Text>}
              description={selected.aiSummary}
              type="info"
              showIcon
              style={{ marginBottom: 12 }}
            />

            {/* AI Suggested Response — real LLM draft for the agent to review (HITL).
                If the AI could not generate a draft, show an honest fallback message. */}
            <Alert
              message={<Text strong>AI Suggested Response</Text>}
              description={
                selected.aiResponse
                  ? selected.aiResponse
                  : 'The AI was unable to generate a suggested response for this ticket. Please review the conversation above and write a custom reply below.'
              }
              type={selected.aiResponse ? 'success' : 'warning'}
              showIcon
              style={{ marginBottom: 12 }}
            />

            {/* Reply sent to customer — shown after agent approves AI response or sends custom reply */}
            {selected.agentReplySent && (
              <Alert
                message={
                  <Text strong>
                    {selected.resolveAction === 'approved'
                      ? 'AI Response Approved — Sent to Customer'
                      : 'Custom Reply Sent to Customer'}
                  </Text>
                }
                description={selected.agentReplySent}
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            {/* Persistent status banner — shown whenever ticket is no longer Open.
                This persists even after switching to another ticket and back,
                because it reads from ticket.status (local state) not actionDone. */}
            {selected.status === 'Resolved' && (
              <Alert message="This ticket has been resolved." type="success" showIcon style={{ marginBottom: 12 }} />
            )}
            {selected.status === 'Closed' && (
              <Alert message="This ticket has been closed." type="warning" showIcon style={{ marginBottom: 12 }} />
            )}

            {/* Transient error feedback (only visible immediately after a failed action) */}
            {actionDone === 'error' && (
              <Alert message="Action failed. Please check if the API server is running." type="error" showIcon style={{ marginBottom: 12 }} />
            )}

            {/* Custom reply box — only shown when Open and agent clicks Write Custom Reply */}
            {selected.status === 'Open' && showReplyBox && (
              <div style={{ marginBottom: 12 }}>
                <TextArea
                  rows={3}
                  value={customReply}
                  onChange={e => setCustomReply(e.target.value)}
                  placeholder="Type your custom reply to the customer..."
                  style={{ marginBottom: 8 }}
                />
                <Space>
                  <Button type="primary" onClick={handleSendReply} disabled={!customReply.trim()} loading={actionLoading}>
                    Send Reply
                  </Button>
                  <Button onClick={() => setShowReplyBox(false)}>Cancel</Button>
                </Space>
              </div>
            )}

            {/* Action buttons — only shown when ticket is still Open.
                Gated on ticket.status (not actionDone) so they stay hidden
                even after switching to another ticket and back. */}
            {selected.status === 'Open' && (
              <Space>
                <Button
                  type="primary"
                  onClick={handleApprove}
                  loading={actionLoading}
                  disabled={!selected.aiResponse || actionLoading}
                  title={!selected.aiResponse ? 'No AI draft available to approve' : undefined}
                >
                  Approve AI Response
                </Button>
                <Button onClick={() => setShowReplyBox(true)} disabled={showReplyBox || actionLoading}>
                  Write Custom Reply
                </Button>
                <Button type="primary" danger onClick={handleClose} loading={actionLoading}>
                  Close Ticket
                </Button>
              </Space>
            )}

          </Card>
        )}
      </div>

    </div>
  )
}

export default AgentDashboard
