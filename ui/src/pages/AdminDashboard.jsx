import { Typography, Card, Row, Col, Statistic, Table, Tag, Alert, Space, Badge } from 'antd'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'

const { Title, Text } = Typography

// ── Mock data ──────────────────────────────────────────────────────────────────

const dailyInteractions = [
  { day: 'Mon', interactions: 18 },
  { day: 'Tue', interactions: 24 },
  { day: 'Wed', interactions: 31 },
  { day: 'Thu', interactions: 22 },
  { day: 'Fri', interactions: 38 },
  { day: 'Sat', interactions: 14 },
  { day: 'Sun', interactions: 10 },
]

const categoryData = [
  { name: 'Billing',   value: 35 },
  { name: 'Technical', value: 28 },
  { name: 'General',   value: 25 },
  { name: 'Other',     value: 12 },
]
const PIE_COLORS = ['#1677ff', '#52c41a', '#faad14', '#ff4d4f']

const routingData = [
  { key: '1', agent: 'Resolution Agent',           share: '45%', count: 71 },
  { key: '2', agent: 'Information Retrieval Agent', share: '30%', count: 47 },
  { key: '3', agent: 'Escalation Agent',            share: '8%',  count: 13 },
]
const routingColumns = [
  { title: 'Agent (post-Triage)',  dataIndex: 'agent',  key: 'agent' },
  { title: 'Share',                dataIndex: 'share',  key: 'share',  width: 80 },
  { title: 'Count',                dataIndex: 'count',  key: 'count',  width: 80 },
]

const knowledgeGaps = [
  '"Refund timeline for international orders" — asked 12 times, no clear answer in knowledge base.',
  '"API key rotation" — asked 8 times, documentation not indexed.',
  '"Student discount eligibility" — asked 6 times, policy not available in system.',
]

const backgroundAgents = [
  { name: 'Security & Compliance Agent', detail: 'No threats detected in last 24h' },
  { name: 'Verification Agent',          detail: '0 hallucinations flagged today'  },
  { name: 'Analytics Agent',             detail: '157 interactions logged'         },
]

const xaiTraces = [
  {
    key: '1',
    ticketId: 'TKT-12345',
    agent: 'Triage Agent',
    category: 'Billing',
    reason: 'Keywords "charged twice" and "subscription" matched billing intent with 94% confidence.',
    timestamp: '2026-03-05 09:14',
  },
  {
    key: '2',
    ticketId: 'TKT-12346',
    agent: 'Triage → Resolution → Escalation',
    category: 'Technical',
    reason: '"Cannot log in" matched account access intent. Routed to Resolution Agent; escalated after 2 failed resolution attempts.',
    timestamp: '2026-03-05 09:32',
  },
  {
    key: '3',
    ticketId: 'TKT-12347',
    agent: 'Information Retrieval Agent',
    category: 'General Inquiry',
    reason: 'Query matched return policy documents in knowledge base with similarity score 0.87.',
    timestamp: '2026-03-05 10:05',
  },
  {
    key: '4',
    ticketId: 'TKT-12348',
    agent: 'Escalation Agent',
    category: 'Order Tracking',
    reason: 'Sentiment score −0.82 (Frustrated). Confidence threshold not met for automated resolution. Escalated per policy.',
    timestamp: '2026-03-05 10:22',
  },
]
const xaiColumns = [
  { title: 'Ticket',          dataIndex: 'ticketId',  key: 'ticketId',  width: 110 },
  { title: 'Agent Path',      dataIndex: 'agent',     key: 'agent',     width: 220 },
  { title: 'Category',        dataIndex: 'category',  key: 'category',  width: 130 },
  { title: 'Decision Reason', dataIndex: 'reason',    key: 'reason'                },
  { title: 'Time',            dataIndex: 'timestamp', key: 'timestamp', width: 155 },
]

// ── Page component ─────────────────────────────────────────────────────────────
function AdminDashboard() {
  return (
    <div>
      <Title level={3} style={{ marginBottom: 20 }}>AI Admin Dashboard</Title>

      {/* ── Section 1: Summary stat cards ──────────────────────────── */}
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Interactions (This Week)" value={157} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Resolved by AI" value={92} suffix="%" valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Escalation Rate" value={8} suffix="%" valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Avg AI Response Time" value={1.4} suffix="s" valueStyle={{ color: '#1677ff' }} />
          </Card>
        </Col>
      </Row>

      {/* ── Section 2: Charts ──────────────────────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>

        {/* Line chart: daily interaction trend */}
        <Col span={16}>
          <Card title="Interactions This Week">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={dailyInteractions} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="interactions"
                  stroke="#1677ff"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Pie chart: request categories */}
        <Col span={8}>
          <Card title="Requests by Category">
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name} ${value}%`}
                  labelLine={false}
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* ── Section 3: Agent routing + Knowledge gaps ──────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>

        {/* Routing table */}
        <Col span={12}>
          <Card
            title="Agent Routing (post-Triage)"
            extra={<Text type="secondary" style={{ fontSize: 12 }}>Triage Agent handles 100% of requests first</Text>}
          >
            <Table
              dataSource={routingData}
              columns={routingColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>

        {/* Knowledge gaps */}
        <Col span={12}>
          <Card title="Knowledge Gap Alerts">
            <Space direction="vertical" style={{ width: '100%' }}>
              {knowledgeGaps.map((gap, i) => (
                <Alert key={i} message={gap} type="warning" showIcon />
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* ── Section 4: Background agent health ─────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Background Agent Health">
            <Row gutter={[16, 0]}>
              {backgroundAgents.map((agent, i) => (
                <Col span={8} key={i}>
                  <Space>
                    <Badge status="success" />
                    <div>
                      <Text strong style={{ display: 'block' }}>{agent.name}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>{agent.detail}</Text>
                    </div>
                  </Space>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* ── Section 5: XAI decision traces ─────────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16, marginBottom: 24 }}>
        <Col span={24}>
          <Card title="XAI Decision Traces">
            <Table
              dataSource={xaiTraces}
              columns={xaiColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

    </div>
  )
}

export default AdminDashboard
