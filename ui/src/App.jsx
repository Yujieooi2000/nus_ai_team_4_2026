import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ConfigProvider, Layout } from 'antd'
import NavBar from './components/NavBar'
import CustomerChat from './pages/CustomerChat'
import AgentDashboard from './pages/AgentDashboard'
import AdminDashboard from './pages/AdminDashboard'

const { Content } = Layout

function App() {
  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#1677ff' } }}>
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <NavBar />
          <Content style={{ padding: '24px', background: '#f5f5f5' }}>
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
