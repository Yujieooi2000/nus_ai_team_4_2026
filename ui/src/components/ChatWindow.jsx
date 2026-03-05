import { useState, useRef, useEffect } from 'react'
import { Input, Button, Tag, Typography, Space } from 'antd'

const { Text } = Typography

// Mock AI responses that cycle through on each message sent.
// Each entry simulates a different agent handling the request.
const MOCK_RESPONSES = [
  {
    text: "I can help you track your order! Order #ORD-78234 is currently in transit and estimated to arrive within 3–5 business days.",
    agent: "Resolution Agent",
    category: "Order Tracking",
    priority: "Low",
  },
  {
    text: "To reset your password, click 'Forgot Password' on the login page. You'll receive a reset email within 2 minutes.",
    agent: "Information Retrieval Agent",
    category: "Account Support",
    priority: "Medium",
  },
  {
    text: "I can see a duplicate charge on your account. I'm initiating a refund now — it should appear within 3–5 business days.",
    agent: "Resolution Agent",
    category: "Billing",
    priority: "High",
  },
  {
    text: "Our standard shipping takes 3–5 business days. Express (1–2 days) is available at checkout. We accept Visa, Mastercard, and PayPal.",
    agent: "Information Retrieval Agent",
    category: "General Inquiry",
    priority: "Low",
  },
]

const PRIORITY_COLORS = { High: 'red', Medium: 'orange', Low: 'green' }

// Tracks which mock response to show next (cycles through the list)
let responseIndex = 0

function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hello! I'm your AI support assistant. How can I help you today?",
      agent: null,
    },
  ])
  const [input, setInput] = useState('')
  const [escalated, setEscalated] = useState(false)

  // Ref to the bottom of the message list — used to auto-scroll on new messages
  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function sendMessage() {
    if (!input.trim() || escalated) return

    const userMsg = { role: 'user', text: input.trim() }

    // Pick the next mock response in the cycle
    const mock = MOCK_RESPONSES[responseIndex % MOCK_RESPONSES.length]
    responseIndex++
    const aiMsg = {
      role: 'ai',
      text: mock.text,
      agent: mock.agent,
      category: mock.category,
      priority: mock.priority,
    }

    setMessages(prev => [...prev, userMsg, aiMsg])
    setInput('')
  }

  function escalate() {
    const escalationMsg = {
      role: 'ai',
      text: "I've escalated your case to a human support agent. Your ticket ID is TKT-12345. An agent will be with you shortly.",
      agent: "Escalation Agent",
      category: "Human Handoff",
      priority: "High",
    }
    setMessages(prev => [...prev, escalationMsg])
    setEscalated(true)
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
                <Tag color={PRIORITY_COLORS[msg.priority]}>{msg.priority} Priority</Tag>
              </Space>
            )}
          </div>
        ))}

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
          disabled={escalated}
        >
          {escalated ? 'Escalated' : 'Escalate to Human'}
        </Button>
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onPressEnter={sendMessage}
          placeholder={escalated ? 'This chat has been escalated to a human agent.' : 'Type your message...'}
          disabled={escalated}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          onClick={sendMessage}
          disabled={escalated || !input.trim()}
        >
          Send
        </Button>
      </div>

    </div>
  )
}

export default ChatWindow
