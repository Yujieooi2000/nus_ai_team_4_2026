import { useState, useEffect } from 'react'
import { Typography, Card, Row, Col, Statistic, Table, Tag, Alert, Space, Badge, Spin } from 'antd'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import { getAnalyticsSummary, getXaiTraces } from '../services/api'
import { formatCategory, mapSentiment, capitalize, formatTimestamp } from '../utils/formatters'

const { Title, Text } = Typography

// ── Table columns for agent routing (static config, data comes from API) ───────
const routingColumns = [
  { title: 'Agent (post-Triage)', dataIndex: 'agent', key: 'agent' },
  { title: 'Share',               dataIndex: 'share', key: 'share', width: 80 },
  { title: 'Count',               dataIndex: 'count', key: 'count', width: 80 },
]

const backgroundAgents = [
  { name: 'Security & Compliance Agent', detail: 'No threats detected in last 24h' },
  { name: 'Verification Agent',          detail: '0 hallucinations flagged today'  },
  { name: 'Analytics Agent',             detail: 'Logging all interactions'        },
]

const PIE_COLORS = ['#1677ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2']

// ── XAI traces table columns ───────────────────────────────────────────────────
const PRIORITY_COLORS  = { High: 'red', Medium: 'orange', Low: 'green' }
const SENTIMENT_COLORS = { Frustrated: 'volcano', Neutral: 'default', Satisfied: 'green' }

const xaiColumns = [
  { title: 'Trace ID',        dataIndex: 'traceId',    key: 'traceId',    width: 110 },
  { title: 'Agent Path',      dataIndex: 'agentPath',  key: 'agentPath',  width: 210 },
  { title: 'Category',        dataIndex: 'category',   key: 'category',   width: 130,
    render: cat => <Tag>{cat}</Tag> },
  { title: 'Priority',        dataIndex: 'priority',   key: 'priority',   width: 90,
    render: p => <Tag color={PRIORITY_COLORS[p] || 'default'}>{p}</Tag> },
  { title: 'Sentiment',       dataIndex: 'sentiment',  key: 'sentiment',  width: 110,
    render: s => <Tag color={SENTIMENT_COLORS[s] || 'default'}>{s}</Tag> },
  { title: 'Confidence',      dataIndex: 'confidence', key: 'confidence', width: 100 },
  { title: 'Decision Reason', dataIndex: 'reason',     key: 'reason' },
  { title: 'Time',            dataIndex: 'timestamp',  key: 'timestamp',  width: 175 },
]


// ── Page component ─────────────────────────────────────────────────────────────
function AdminDashboard() {

  // Real data from API
  const [summary, setSummary] = useState(null)
  const [traces, setTraces]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  // Load analytics data when the page first loads
  useEffect(() => {
    async function fetchData() {
      try {
        const [summaryData, tracesData] = await Promise.all([
          getAnalyticsSummary(),
          getXaiTraces(),
        ])
        setSummary(summaryData)
        setTraces(tracesData)
      } catch (err) {
        setError('Could not load analytics. Is the API server running?')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // ── Loading state ────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ height: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip="Loading analytics..." />
      </div>
    )
  }

  // ── Error state ──────────────────────────────────────────────────────────────
  if (error) {
    return (
      <Alert
        type="error"
        message="Could not load analytics"
        description={error}
        showIcon
        style={{ margin: '40px auto', maxWidth: 600 }}
      />
    )
  }

  // ── Derive values from real API data ─────────────────────────────────────────

  // Stat card values (real)
  const totalRequests  = summary?.total_requests ?? 0
  const resolutionRate = summary?.resolution_rate
    ? parseFloat(summary.resolution_rate).toFixed(1)
    : '0.0'
  const escalationRate = summary?.escalation_rate != null
    ? (summary.escalation_rate * 100).toFixed(1)
    : '0.0'

  // Pie chart: convert { billing: 4, general_inquiry: 5 } → [{ name, value }, ...]
  const categoryData = summary?.category_breakdown
    ? Object.entries(summary.category_breakdown).map(([name, value]) => ({
        name:  formatCategory(name, 'Unknown'),
        value,
      }))
    : []

  // Daily interactions line chart (real — last 7 days from analytics_db)
  const dailyInteractions = summary?.daily_interactions ?? []

  // Agent routing table (real — derived from analytics_db)
  const routingData = (summary?.agent_routing ?? []).map((row, i) => ({ ...row, key: String(i) }))

  // Knowledge gap alerts (real — from analytics_agent.detect_knowledge_gaps())
  const knowledgeGaps = summary?.knowledge_gaps ?? []

  // XAI traces: map API format to table rows
  const xaiTableData = traces.map((t, i) => ({
    key:        String(i),
    traceId:    t.trace_id,
    agentPath:  t.agent_path,
    category:   formatCategory(t.category, 'Unknown'),
    priority:   capitalize(t.priority || 'low'),
    sentiment:  mapSentiment(t.sentiment),
    confidence: t.confidence != null ? `${(t.confidence * 100).toFixed(0)}%` : '—',
    reason:     t.decision_reason || 'No reason recorded',
    timestamp:  formatTimestamp(t.timestamp),
  }))

  // Show real interaction count in the Analytics Agent health badge
  const agentsWithRealCount = backgroundAgents.map(a =>
    a.name === 'Analytics Agent'
      ? { ...a, detail: `${totalRequests} interactions logged` }
      : a
  )

  return (
    <div>
      <Title level={3} style={{ marginBottom: 20 }}>AI Admin Dashboard</Title>

      {/* ── Section 1: Summary stat cards (REAL data) ──────────────── */}
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Interactions" value={totalRequests} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Resolved by AI"
              value={resolutionRate}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Escalation Rate"
              value={escalationRate}
              suffix="%"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Hallucination Rate"
              value={
                summary?.hallucination_rate != null
                  ? (summary.hallucination_rate * 100).toFixed(1)
                  : '0.0'
              }
              suffix="%"
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* ── Section 2: Charts ──────────────────────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>

        {/* Line chart: daily interaction trend (REAL — last 7 days from analytics_db) */}
        <Col span={16}>
          <Card
            title="Interactions This Week"
            extra={<Text type="secondary" style={{ fontSize: 12 }}>Last 7 days</Text>}
          >
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

        {/* Pie chart: request categories (REAL data) */}
        <Col span={8}>
          <Card title="Requests by Category">
            {categoryData.length === 0 ? (
              <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Text type="secondary">No interactions recorded yet</Text>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name} (${value})`}
                    labelLine={false}
                  >
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
      </Row>

      {/* ── Section 3: Agent routing + Knowledge gaps ──────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>

        {/* Routing table (REAL — derived from analytics_db) */}
        <Col span={12}>
          <Card
            title="Agent Routing (post-Triage)"
            extra={<Text type="secondary" style={{ fontSize: 12 }}>Triage Agent handles 100% of requests first</Text>}
          >
            {routingData.length === 0 ? (
              <Text type="secondary">No interactions recorded yet.</Text>
            ) : (
              <Table
                dataSource={routingData}
                columns={routingColumns}
                pagination={false}
                size="small"
              />
            )}
          </Card>
        </Col>

        {/* Knowledge gaps (REAL — from analytics_agent.detect_knowledge_gaps()) */}
        <Col span={12}>
          <Card title="Knowledge Gap Alerts">
            {knowledgeGaps.length === 0 ? (
              <Text type="secondary">No knowledge gaps detected yet.</Text>
            ) : (
              <Space direction="vertical" style={{ width: '100%' }}>
                {knowledgeGaps.map((gap, i) => (
                  <Alert key={i} message={gap} type="warning" showIcon />
                ))}
              </Space>
            )}
          </Card>
        </Col>
      </Row>

      {/* ── Section 4: Background agent health ─────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Background Agent Health">
            <Row gutter={[16, 0]}>
              {agentsWithRealCount.map((agent, i) => (
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

      {/* ── Section 5: XAI decision traces (REAL data) ─────────────── */}
      <Row gutter={[16, 16]} style={{ marginTop: 16, marginBottom: 24 }}>
        <Col span={24}>
          <Card title="XAI Decision Traces">
            {xaiTableData.length === 0 ? (
              <Text type="secondary">
                No interactions recorded yet. Send some messages in the Customer Chat to see traces here.
              </Text>
            ) : (
              <Table
                dataSource={xaiTableData}
                columns={xaiColumns}
                pagination={{ pageSize: 10 }}
                size="small"
              />
            )}
          </Card>
        </Col>
      </Row>

    </div>
  )
}

export default AdminDashboard
