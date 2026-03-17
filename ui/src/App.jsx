import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ConfigProvider, Layout, theme } from 'antd'
import NavBar from './components/NavBar'
import CustomerChat from './pages/CustomerChat'
import AgentDashboard from './pages/AgentDashboard'
import AdminDashboard from './pages/AdminDashboard'

const { Content } = Layout

function App() {
  // Initialise from localStorage so the user's last preference is remembered on reload
  const [isDark, setIsDark] = useState(
    () => localStorage.getItem('theme') === 'dark'
  )

  // Sync the data-theme attribute on <html> whenever isDark changes.
  // Step O (glass effect) reads this attribute to switch CSS custom properties.
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
  }, [isDark])

  return (
    <ConfigProvider theme={{
      algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
      token: {
        colorPrimary:         '#1677ff',
        fontFamily:           "'Atkinson Hyperlegible Next', 'Atkinson Hyperlegible', sans-serif",
        // ── Tiered dark mode colours ──────────────────────────────────────────
        // Page background (#000000) is true OLED black — no content sits directly
        // on it; it fills the gaps between cards so OLED pixels are fully off.
        // Card surfaces use a transparent glass colour so backdrop-filter blurs
        // the page background through them (set below in components.Card).
        colorBgBase:          isDark ? '#000000' : '#ffffff',
        colorBgElevated:      isDark ? '#1a1a1a' : '#ffffff',
        colorText:            isDark ? '#f0f0f0' : '#1a1a1a',
        colorTextSecondary:   isDark ? '#a0a0a0' : '#595959',
      },
      components: {
        // ── Glass card backgrounds ────────────────────────────────────────────
        // Translucent so backdrop-filter (set in index.css) blurs through the card.
        // Dark:  barely-visible glass floating on OLED black
        // Light: frosted white floating on the light grey page background
        Card: {
          colorBgContainer: isDark
            ? 'rgba(255, 255, 255, 0.14)'
            : 'rgba(255, 255, 255, 0.72)',
        },
      },
    }}>
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <NavBar isDark={isDark} toggleTheme={() => setIsDark(d => !d)} />
          <Content style={{
            padding:    '24px',
            background: isDark
              ? '#000000'
              : 'linear-gradient(135deg, #eef2ff 0%, #f5f0ff 40%, #fff0f6 100%)',
            transition: 'background 0.3s ease',
          }}>
            <Routes>
              <Route path="/"      element={<CustomerChat />} />
              <Route path="/agent" element={<AgentDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
            </Routes>
          </Content>
        </Layout>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
