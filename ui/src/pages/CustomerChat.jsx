import { Card, Typography } from 'antd'
import ChatWindow from '../components/ChatWindow'

const { Title, Text } = Typography

function CustomerChat() {
  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <Title level={3} style={{ marginBottom: 16 }}>Customer Support Chat</Title>

      <Card
        style={{
          borderRadius: 12,
          overflow: 'hidden',
          boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
          height: 580,
        }}
        styles={{ body: { padding: 0, height: '100%', display: 'flex', flexDirection: 'column' } }}
      >
        {/* Chat header bar */}
        <div style={{ padding: '14px 18px', background: '#1677ff' }}>
          <Text strong style={{ color: 'white', fontSize: 15, display: 'block' }}>
            AI Support Assistant
          </Text>
          <Text style={{ color: 'rgba(255,255,255,0.75)', fontSize: 12 }}>
            Powered by multi-agent AI
          </Text>
        </div>

        {/* Chat window — fills remaining height */}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <ChatWindow />
        </div>
      </Card>
    </div>
  )
}

export default CustomerChat
