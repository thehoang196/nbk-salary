import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Space, Typography } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  TeamOutlined,
  BookOutlined,
  CalendarOutlined,
  DollarOutlined,
  FileTextOutlined,
  TableOutlined,
  GiftOutlined,
  AppstoreOutlined,
  BankOutlined,
  SafetyCertificateOutlined,
  SolutionOutlined,
  ReadOutlined,
  MoneyCollectOutlined,
  UsergroupAddOutlined,
} from '@ant-design/icons';
import useAuthStore from '../store/authStore';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

/**
 * Build menu items based on user role.
 * - Admin: sees all menu items including Quản lý user
 * - Accountant: sees data entry and salary-related items (no user management)
 * - Viewer: sees only reports and dashboard (read-only)
 */
function getMenuItems(role) {
  const allItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      roles: ['admin', 'accountant', 'viewer'],
    },
    {
      key: '/danh-muc',
      icon: <AppstoreOutlined />,
      label: 'Giáo viên',
      roles: ['admin', 'accountant'],
      children: [
        { key: '/danh-muc?tab=don-vi', icon: <BankOutlined />, label: 'Đơn vị' },
        { key: '/danh-muc?tab=chuc-vu', icon: <SafetyCertificateOutlined />, label: 'Chức vụ' },
        { key: '/danh-muc?tab=cap-bac-ql', icon: <SolutionOutlined />, label: 'Cấp bậc QL' },
        { key: '/danh-muc?tab=nghiep-vu', icon: <ReadOutlined />, label: 'Nghiệp vụ' },
        { key: '/danh-muc?tab=kiem-nhiem', icon: <TeamOutlined />, label: 'Kiêm nhiệm' },
        { key: '/danh-muc?tab=mon-hoc', icon: <BookOutlined />, label: 'Môn học' },
        { key: '/danh-muc?tab=he-so-luong', icon: <MoneyCollectOutlined />, label: 'Hệ số lương' },
        { key: '/danh-muc?tab=don-gia-day', icon: <DollarOutlined />, label: 'Đơn giá dạy' },
      ],
    },
    {
      key: '/nhan-vien',
      icon: <TeamOutlined />,
      label: 'Nhân viên',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/tkb',
      icon: <BookOutlined />,
      label: 'Thời khóa biểu',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/tiet-ngoai',
      icon: <TableOutlined />,
      label: 'Tiết dạy ngoài',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/ho-tro-luong',
      icon: <GiftOutlined />,
      label: 'Hỗ trợ lương',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/cham-cong',
      icon: <CalendarOutlined />,
      label: 'Chấm công',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/bang-luong',
      icon: <DollarOutlined />,
      label: 'Bảng lương',
      roles: ['admin', 'accountant'],
    },
    {
      key: '/bao-cao',
      icon: <FileTextOutlined />,
      label: 'Báo cáo',
      roles: ['admin', 'accountant', 'viewer'],
    },
    {
      key: '/misa-import',
      icon: <FileTextOutlined />,
      label: 'Import MISA',
      roles: ['admin', 'accountant', 'hr'],
    },
    {
      key: '/quan-ly-user',
      icon: <UsergroupAddOutlined />,
      label: 'Quản lý user',
      roles: ['admin'],
    },
  ];

  const userRole = (role || '').toLowerCase();

  return allItems
    .filter((item) => item.roles.includes(userRole))
    .map(({ roles, ...item }) => {
      // Remove roles property from items before passing to Menu
      if (item.children) {
        return { ...item, children: item.children.map(({ roles: _r, ...child }) => child) };
      }
      return item;
    });
}

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = getMenuItems(user?.role);

  // Determine selected key from pathname + search
  const currentKey = location.pathname + location.search;
  // For submenu open keys
  const openKeys = location.pathname.startsWith('/danh-muc') ? ['/danh-muc'] : [];

  const handleMenuClick = ({ key }) => {
    // Handle menu items with query params (e.g., /danh-muc?tab=don-vi)
    if (key.includes('?')) {
      const [path, query] = key.split('?');
      navigate(`${path}?${query}`);
    } else {
      navigate(key);
    }
  };

  const userMenuItems = {
    items: [
      {
        key: 'user-info',
        label: (
          <div style={{ padding: '4px 0' }}>
            <div style={{ fontWeight: 500 }}>{user?.full_name || 'User'}</div>
            <div style={{ fontSize: 12, color: '#888' }}>
              {user?.role === 'admin' ? 'Quản trị viên' : user?.role === 'accountant' ? 'Kế toán' : 'Xem báo cáo'}
            </div>
          </div>
        ),
        disabled: true,
      },
      { type: 'divider' },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: 'Đăng xuất',
        onClick: logout,
      },
    ],
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 48,
            margin: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Text
            strong
            style={{
              color: '#fff',
              fontSize: collapsed ? 14 : 18,
              whiteSpace: 'nowrap',
            }}
          >
            {collapsed ? 'NBK' : 'NBK Salary'}
          </Text>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[currentKey, location.pathname]}
          defaultOpenKeys={openKeys}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <Dropdown menu={userMenuItems} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} />
              <span>{user?.full_name || 'User'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16, padding: 24, background: '#fff', borderRadius: 8, minHeight: 360 }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
}
