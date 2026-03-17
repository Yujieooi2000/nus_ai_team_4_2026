import { Layout, Menu, Typography, Button } from 'antd'
import { SunOutlined, MoonOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Header } = Layout
const { Text } = Typography

const navItems = [
  { key: '/',      label: 'Customer Chat' },
  { key: '/agent', label: 'Agent Dashboard' },
  { key: '/admin', label: 'Admin Dashboard' },
]

function NavBar({ isDark, toggleTheme }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
      <Text strong style={{ color: 'white', fontSize: 18, marginRight: 48, whiteSpace: 'nowrap' }}>
        AI Support System
      </Text>
      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={navItems}
        onClick={({ key }) => navigate(key)}
        style={{ flex: 1, minWidth: 0 }}
      />
      {/* Dark / Light mode toggle — sun icon in dark mode, moon icon in light mode */}
      <Button
        type="text"
        icon={isDark ? <SunOutlined /> : <MoonOutlined />}
        onClick={toggleTheme}
        title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        style={{ color: 'white', marginLeft: 16, fontSize: 16 }}
      />
    </Header>
  )
}

export default NavBar
