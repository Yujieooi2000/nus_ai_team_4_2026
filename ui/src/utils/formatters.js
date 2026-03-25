// Shared formatting utilities used across multiple pages/components.

export const PRIORITY_COLORS  = { High: 'red', Medium: 'orange', Low: 'green' }
export const SENTIMENT_COLORS = { Frustrated: 'volcano', Neutral: 'default', Satisfied: 'green' }
export const STATUS_COLORS    = { Open: 'blue', 'In Progress': 'orange', Resolved: 'green', Closed: 'default' }

export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function formatCategory(cat, fallback = 'General') {
  if (!cat) return fallback
  return cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export function mapSentiment(sentiment) {
  const map = { negative: 'Frustrated', neutral: 'Neutral', positive: 'Satisfied' }
  return map[sentiment] || 'Neutral'
}

// Formats an ISO timestamp as "DD MMM YYYY, HH:mm SGT"
// e.g. "24 Mar 2026, 14:30 SGT"
export function formatTimestamp(isoString) {
  if (!isoString) return '—'
  // Treat timestamps without timezone info as UTC
  const ts = isoString.includes('+') || isoString.endsWith('Z') ? isoString : isoString + 'Z'
  const date = new Date(ts)
  const datePart = date.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric', timeZone: 'Asia/Singapore',
  })
  const timePart = date.toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Singapore',
  })
  return `${datePart}, ${timePart} SGT`
}
