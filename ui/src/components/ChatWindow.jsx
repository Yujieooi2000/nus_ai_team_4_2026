import { useState, useRef, useEffect } from 'react'
import { Input, Button, Tag, Typography, Space, Spin } from 'antd'
import { sendChatMessage } from '../services/api'

const { Text } = Typography

// Colour map for priority tags
const PRIORITY_COLORS = { High: 'red', Medium: 'orange', Low: 'green' }

// ── Helper: format agent name from API ("ResolutionAgent" → "Resolution Agent") ──
const AGENT_DISPLAY_NAMES = {
  ResolutionAgent:            'Resolution Agent',
  InformationRetrievalAgent:  'Information Retrieval Agent',
  EscalationAgent:            'Escalation Agent',
  SecurityComplianceAgent:    'Security Agent',
}
function formatAgentName(name) {
  return AGENT_DISPLAY_NAMES[name] || name || 'AI Agent'
}

// ── Helper: format category from API ("technical_support" → "Technical Support") ──
function formatCategory(cat) {
  if (!cat) return 'General'
  return cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

// ── Helper: capitalise first letter ("high" → "High") ──
function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}


function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hello! I'm your AI support assistant. How can I help you today?",
      agent: null,
    },
  ])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)  // true while waiting for API response
  const [escalated, setEscalated] = useState(false)

  // sessionId is generated once when the component mounts and never changes.
  // Using useRef means it survives re-renders without triggering them.
  const sessionId = useRef(`session_${Date.now()}_${Math.random().toString(36).slice(2)}`)

  // Ref to the bottom of the message list — used to auto-scroll on new messages
  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])


  async function sendMessage() {
    if (!input.trim() || escalated || loading) return

    const userText = input.trim()
    const userMsg  = { role: 'user', text: userText }

    // Show user message immediately, clear the input, show loading state
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      // Call the FastAPI backend — this runs the full 7-agent pipeline
      const result = await sendChatMessage(userText, sessionId.current)

      const aiMsg = {
        role:     'ai',
        text:     result.message || 'I received your message.',
        agent:    formatAgentName(result.agent),
        category: formatCategory(result.analysis?.category),
        priority: capitalize(result.analysis?.priority),
      }

      setMessages(prev => [...prev, aiMsg])

      // If the Orchestrator decided to escalate, lock the chat
      if (result.status === 'escalated') {
        setEscalated(true)
      }

    } catch (err) {
      // Show a friendly error if the backend is unreachable
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'Sorry, I am having trouble connecting to the support system. Please try again in a moment.',
        agent: null,
      }])
    } finally {
      setLoading(false)
    }
  }


  async function escalate() {
    if (loading) return
    // Send an explicit human-request message — the EscalationAgent detects this
    // and triggers a proper escalation through the Orchestrator pipeline.
    setLoading(true)
    try {
      const result = await sendChatMessage(
        'I want to speak to a human agent.',
        sessionId.current
      )
      const escalationMsg = {
        role:     'ai',
        text:     result.message || 'Connecting you to a human agent.',
        agent:    formatAgentName(result.agent),
        category: 'Human Handoff',
        priority: 'High',
      }
      setMessages(prev => [...prev, escalationMsg])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'Your case has been escalated. A human agent will be with you shortly.',
        agent: 'Escalation Agent',
        category: 'Human Handoff',
        priority: 'High',
      }])
    } finally {
      setEscalated(true)
      setLoading(false)
    }
  }


  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      {/* ── Message list ───────────────────────────────────────────── */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {/* Chat bubble */}
            <div style={{
              maxWidth: '70%',
              padding: '10px 14px',
              borderRadius: msg.role === 'user'
                ? '18px 18px 4px 18px'
                : '18px 18px 18px 4px',
              background: msg.role === 'user' ? '#1677ff' : '#ffffff',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            }}>
              <Text style={{ color: msg.role === 'user' ? 'white' : '#222' }}>
                {msg.text}
              </Text>
            </div>

            {/* Agent metadata tags — shown below AI messages only */}
            {msg.agent && (
              <Space size={4} style={{ marginTop: 6 }}>
                <Tag color="blue">{msg.agent}</Tag>
                <Tag>{msg.category}</Tag>
                {msg.priority && (
                  <Tag color={PRIORITY_COLORS[msg.priority] || 'default'}>
                    {msg.priority} Priority
                  </Tag>
                )}
              </Space>
            )}
          </div>
        ))}

        {/* Loading indicator — shown while waiting for API response */}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Spin size="small" />
            <Text type="secondary" style={{ fontSize: 12 }}>AI is thinking...</Text>
          </div>
        )}

        {/* Invisible anchor at the bottom for auto-scroll */}
        <div ref={bottomRef} />
      </div>

      {/* ── Input area ─────────────────────────────────────────────── */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid #e8e8e8',
        background: '#fafafa',
        display: 'flex',
        gap: 8,
        alignItems: 'center',
      }}>
        <Button
          danger
          onClick={escalate}
          disabled={escalated || loading}
        >
          {escalated ? 'Escalated' : 'Escalate to Human'}
        </Button>
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onPressEnter={sendMessage}
          placeholder={
            escalated
              ? 'This chat has been escalated to a human agent.'
              : loading
              ? 'Waiting for response...'
              : 'Type your message...'
          }
          disabled={escalated || loading}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          onClick={sendMessage}
          disabled={escalated || loading || !input.trim()}
          loading={loading}
        >
          Send
        </Button>
      </div>

    </div>
  )
}

export default ChatWindow
