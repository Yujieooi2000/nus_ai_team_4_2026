import { Card, Tag, Typography, Space } from 'antd'
import { PRIORITY_COLORS, SENTIMENT_COLORS, STATUS_COLORS } from '../utils/formatters'

const { Text } = Typography

// A single row in the ticket queue (left panel).
// Props:
//   ticket   — the ticket data object
//   selected — boolean, true when this ticket is currently open in the right panel
//   onClick  — function called when the card is clicked
function TicketCard({ ticket, selected, onClick }) {
  return (
    <Card
      size="small"
      onClick={onClick}
      style={{
        cursor: 'pointer',
        marginBottom: 8,
        borderRadius: 8,
        // Selected: blue border + tinted bg. Non-selected: let theme colorBgContainer
        // and the global .ant-card CSS rule handle border + background (same as Admin Dashboard).
        ...(selected && {
          border: '2px solid #1677ff',
          background: 'var(--ticket-card-bg-selected)',
        }),
      }}
    >
      {/* Top row: ticket ID + status badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text strong style={{ fontSize: 13 }}>{ticket.id}</Text>
        <Tag color={STATUS_COLORS[ticket.status]}>{ticket.status}</Tag>
      </div>

      {/* Customer name */}
      <Text style={{ display: 'block', marginTop: 2, fontSize: 13 }}>
        {ticket.customer}
      </Text>

      {/* Short preview of the issue */}
      <Text type="secondary" style={{ display: 'block', fontSize: 12, marginTop: 2 }}>
        {ticket.preview}
      </Text>

      {/* Priority + sentiment tags */}
      <Space size={4} style={{ marginTop: 6 }}>
        <Tag color={PRIORITY_COLORS[ticket.priority]}  style={{ fontSize: 11 }}>{ticket.priority}</Tag>
        <Tag color={SENTIMENT_COLORS[ticket.sentiment]} style={{ fontSize: 11 }}>{ticket.sentiment}</Tag>
      </Space>

      {/* Timestamp */}
      <Text type="secondary" style={{ display: 'block', fontSize: 11, marginTop: 4 }}>
        {ticket.timestamp}
      </Text>
    </Card>
  )
}

export default TicketCard
