// Shared formatting utilities used across multiple pages/components.

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
