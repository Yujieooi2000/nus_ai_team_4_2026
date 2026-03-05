import { useState } from 'react'
import { Typography, Tag, Button, Input, Alert, Empty, Space, Divider, Card } from 'antd'
import TicketCard from '../components/TicketCard'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

// ── Colour maps ────────────────────────────────────────────────────────────────
const PRIORITY_COLORS  = { High: 'red',      Medium: 'orange',  Low: 'green'     }
const SENTIMENT_COLORS = { Frustrated: 'volcano', Neutral: 'default', Satisfied: 'green' }

// ── Mock ticket data ───────────────────────────────────────────────────────────
// This will be replaced by a real API call in Step 7.
const INITIAL_TICKETS = [
  {
    id: 'TKT-12345',
    customer: 'Jane Doe',
    priority: 'High',
    sentiment: 'Frustrated',
    category: 'Billing',
    timestamp: '2026-03-05  09:14',
    status: 'Open',
    preview: 'Charged twice for my subscription...',
    aiSummary:
      'Customer reports a duplicate charge on their account for the monthly subscription. AI confidence was low due to account access limitations — escalated for human review.',
    conversation: [
      { role: 'user', text: 'I was charged twice for my subscription this month!' },
      { role: 'ai',   text: 'I understand your frustration. Let me look into this billing issue for you.' },
      { role: 'user', text: 'This is really unacceptable. I need this fixed immediately.' },
      { role: 'ai',   text: 'I can see your account details but need elevated access to process the refund. Escalating to a human agent now.' },
    ],
    aiResponse:
      'I sincerely apologize for the duplicate charge. I have initiated a refund of $29.99 to your account. It will appear within 3–5 business days.',
  },
  {
    id: 'TKT-12346',
    customer: 'Marcus Tan',
    priority: 'Medium',
    sentiment: 'Neutral',
    category: 'Technical',
    timestamp: '2026-03-05  09:32',
    status: 'Open',
    preview: 'Unable to log in after password change...',
    aiSummary:
      'Customer is experiencing login issues after a recent password change. Standard reset flow was attempted but the customer reports the reset email is not arriving.',
    conversation: [
      { role: 'user', text: 'I cannot log in. I changed my password yesterday and now it does not work.' },
      { role: 'ai',   text: 'I can help you regain access. I have sent a password reset link to your registered email.' },
      { role: 'user', text: 'I have not received any email. I checked spam too.' },
      { role: 'ai',   text: 'I am escalating this to a human agent who can manually verify your account.' },
    ],
    aiResponse:
      'I have manually reset your account and sent a temporary password to your registered email. Please check your inbox within 5 minutes.',
  },
  {
    id: 'TKT-12347',
    customer: 'Priya Sharma',
    priority: 'Low',
    sentiment: 'Neutral',
    category: 'General Inquiry',
    timestamp: '2026-03-05  10:05',
    status: 'Open',
    preview: 'Return policy question for a gift item...',
    aiSummary:
      'Customer is asking about the return policy for a gifted item without an original receipt. AI was uncertain about the gift return exception clause and escalated for confirmation.',
    conversation: [
      { role: 'user', text: "I received a gift I'd like to return but I don't have the receipt. Is that possible?" },
      { role: 'ai',   text: 'Our standard policy requires a receipt for returns. However, there may be exceptions for gifts. Let me connect you with an agent to confirm.' },
    ],
    aiResponse:
      'Good news — we do accept gift returns without a receipt within 30 days of purchase. Please bring the item to any of our stores and our staff will assist you.',
  },
  {
    id: 'TKT-12348',
    customer: 'David Lim',
    priority: 'High',
    sentiment: 'Frustrated',
    category: 'Order Tracking',
    timestamp: '2026-03-05  10:22',
    status: 'Open',
    preview: 'Order marked delivered but not received...',
    aiSummary:
      "Customer's order is marked as delivered in the system but they report not receiving it. AI could not initiate a reshipment without manual verification from the logistics team.",
    conversation: [
      { role: 'user', text: 'My order says delivered but I never received anything. This is a $200 item!' },
      { role: 'ai',   text: 'I am very sorry to hear this. I can see the delivery was logged at 2:15 PM yesterday. Let me escalate this for investigation.' },
    ],
    aiResponse:
      'I have raised a missing parcel investigation with our courier partner. You will receive an update within 24 hours. If unresolved, we will reship your order at no additional cost.',
  },
]

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
  const [tickets, setTickets]         = useState(INITIAL_TICKETS)
  const [selectedId, setSelectedId]   = useState(null)
  const [showReplyBox, setShowReplyBox] = useState(false)
  const [customReply, setCustomReply] = useState('')
  const [actionDone, setActionDone]   = useState(null) // 'approved' | 'replied' | 'closed'

  const selected = tickets.find(t => t.id === selectedId)

  // Update a ticket's status in the array
  function updateStatus(id, newStatus) {
    setTickets(prev => prev.map(t => t.id === id ? { ...t, status: newStatus } : t))
  }

  function handleSelectTicket(id) {
    setSelectedId(id)
    setShowReplyBox(false)
    setCustomReply('')
    setActionDone(null)
  }

  function handleApprove() {
    updateStatus(selectedId, 'Resolved')
    setActionDone('approved')
  }

  function handleSendReply() {
    if (!customReply.trim()) return
    updateStatus(selectedId, 'Resolved')
    setActionDone('replied')
    setShowReplyBox(false)
  }

  function handleClose() {
    updateStatus(selectedId, 'Closed')
    setActionDone('closed')
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
          {tickets.map(ticket => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              selected={ticket.id === selectedId}
              onClick={() => handleSelectTicket(ticket.id)}
            />
          ))}
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
            <ConversationHistory conversation={selected.conversation} />

            <Divider style={{ margin: '16px 0' }} />

            {/* AI Summary */}
            <Alert
              message={<Text strong>AI Summary</Text>}
              description={selected.aiSummary}
              type="info"
              showIcon
              style={{ marginBottom: 12 }}
            />

            {/* AI Suggested Response */}
            <Alert
              message={<Text strong>AI Suggested Response</Text>}
              description={selected.aiResponse}
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />

            {/* Action result message */}
            {actionDone === 'approved' && (
              <Alert message="AI response approved and sent to customer. Ticket resolved." type="success" showIcon style={{ marginBottom: 12 }} />
            )}
            {actionDone === 'replied' && (
              <Alert message="Custom reply sent to customer. Ticket resolved." type="success" showIcon style={{ marginBottom: 12 }} />
            )}
            {actionDone === 'closed' && (
              <Alert message="Ticket closed without a reply." type="warning" showIcon style={{ marginBottom: 12 }} />
            )}

            {/* Custom reply box */}
            {showReplyBox && (
              <div style={{ marginBottom: 12 }}>
                <TextArea
                  rows={3}
                  value={customReply}
                  onChange={e => setCustomReply(e.target.value)}
                  placeholder="Type your custom reply to the customer..."
                  style={{ marginBottom: 8 }}
                />
                <Space>
                  <Button type="primary" onClick={handleSendReply} disabled={!customReply.trim()}>
                    Send Reply
                  </Button>
                  <Button onClick={() => setShowReplyBox(false)}>Cancel</Button>
                </Space>
              </div>
            )}

            {/* Action buttons — hidden once an action is taken */}
            {!actionDone && (
              <Space>
                <Button type="primary" onClick={handleApprove}>
                  Approve AI Response
                </Button>
                <Button onClick={() => setShowReplyBox(true)} disabled={showReplyBox}>
                  Write Custom Reply
                </Button>
                <Button danger onClick={handleClose}>
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
