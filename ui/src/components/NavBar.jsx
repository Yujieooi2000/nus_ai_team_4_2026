import { Layout, Menu, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'

const { Header } = Layout
const { Text } = Typography

const navItems = [
  { key: '/',      label: 'Customer Chat' },
  { key: '/agent', label: 'Agent Dashboard' },
  { key: '/admin', label: 'Admin Dashboard' },
]

function NavBar() {
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
    </Header>
  )
}

export default NavBar
