import React, { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Button, Space, Spin, Typography, Divider } from 'antd';
import {
  TeamOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import useAuthStore from '../store/authStore';

const { Title, Text } = Typography;

export default function Dashboard() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const userRole = user?.role;

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalEmployees: 0,
    gvCount: 0,
    vpCount: 0,
    salaryCalculated: 0,
    salaryPending: 0,
    pendingApprovals: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch employees
      const [allRes, gvRes, vpRes] = await Promise.all([
        api.get('/nhan-vien'),
        api.get('/nhan-vien', { params: { nhom_nv: 'GV' } }),
        api.get('/nhan-vien', { params: { nhom_nv: 'VP' } }),
      ]);

      const totalEmployees = allRes.data?.length || 0;
      const gvCount = gvRes.data?.length || 0;
      const vpCount = vpRes.data?.length || 0;

      // Fetch current month salary data (admin/accountant only)
      let salaryCalculated = 0;
      let salaryPending = 0;
      let pendingApprovals = 0;

      if (userRole === 'admin' || userRole === 'accountant') {
        const now = new Date();
        const thang = now.getMonth() + 1;
        const nam = now.getFullYear();

        try {
          const salaryRes = await api.get(`/luong/bang-luong/${thang}/${nam}`);
          const items = salaryRes.data?.items || [];
          salaryCalculated = items.length;
          salaryPending = totalEmployees - items.length;
          pendingApprovals = items.filter(
            (item) => item.trang_thai === 'draft' || item.trang_thai === 'reviewed'
          ).length;
        } catch {
          // No salary data for current month yet
          salaryPending = totalEmployees;
        }
      }

      setStats({
        totalEmployees,
        gvCount,
        vpCount,
        salaryCalculated,
        salaryPending,
        pendingApprovals,
      });
    } catch {
      // Silently handle errors - dashboard shows 0 values
    } finally {
      setLoading(false);
    }
  };

  // Quick links configuration
  const adminQuickLinks = [
    { title: 'Bảng lương', icon: <DollarOutlined />, path: '/bang-luong' },
    { title: 'Chấm công', icon: <CalendarOutlined />, path: '/cham-cong' },
    { title: 'Nhân viên', icon: <TeamOutlined />, path: '/nhan-vien' },
    { title: 'Báo cáo', icon: <BarChartOutlined />, path: '/bao-cao' },
    { title: 'Thời khóa biểu', icon: <FileTextOutlined />, path: '/tkb' },
    { title: 'Hỗ trợ lương', icon: <DollarOutlined />, path: '/ho-tro-luong' },
  ];

  const userQuickLinks = [
    { title: 'Bảng lương', icon: <DollarOutlined />, path: '/bang-luong' },
    { title: 'Chấm công', icon: <CalendarOutlined />, path: '/cham-cong' },
    { title: 'Nhân viên', icon: <TeamOutlined />, path: '/nhan-vien' },
  ];

  const quickLinks = userRole === 'admin' || userRole === 'accountant'
    ? adminQuickLinks
    : userQuickLinks;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '0' }}>
      <Title level={3}>
        Xin chào, {user?.full_name || 'Người dùng'}!
      </Title>
      <Text type="secondary">
        Hệ thống tính lương THCS Nguyễn Bỉnh Khiêm
      </Text>

      <Divider />

      {/* Summary Statistics Cards */}
      <Title level={5}>Tổng quan</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Tổng nhân viên"
              value={stats.totalEmployees}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Giáo viên (GV)"
              value={stats.gvCount}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable>
            <Statistic
              title="Văn phòng (VP)"
              value={stats.vpCount}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>

        {/* Salary status cards - admin/accountant only */}
        {(userRole === 'admin' || userRole === 'accountant') && (
          <Col xs={24} sm={12} lg={6}>
            <Card hoverable>
              <Statistic
                title="Chờ duyệt lương"
                value={stats.pendingApprovals}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: stats.pendingApprovals > 0 ? '#fa8c16' : '#52c41a' }}
              />
            </Card>
          </Col>
        )}
      </Row>

      {/* Salary status row - admin/accountant only */}
      {(userRole === 'admin' || userRole === 'accountant') && (
        <>
          <Title level={5} style={{ marginTop: 24 }}>
            Lương tháng {new Date().getMonth() + 1}/{new Date().getFullYear()}
          </Title>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={8}>
              <Card hoverable>
                <Statistic
                  title="Đã tính lương"
                  value={stats.salaryCalculated}
                  suffix={`/ ${stats.totalEmployees}`}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Card hoverable>
                <Statistic
                  title="Chưa tính lương"
                  value={stats.salaryPending}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: stats.salaryPending > 0 ? '#fa541c' : '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={8}>
              <Card hoverable>
                <Statistic
                  title="Chờ phê duyệt"
                  value={stats.pendingApprovals}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: stats.pendingApprovals > 0 ? '#fa8c16' : '#52c41a' }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Quick Links */}
      <Title level={5} style={{ marginTop: 24 }}>Truy cập nhanh</Title>
      <Row gutter={[16, 16]}>
        {quickLinks.map((link) => (
          <Col xs={12} sm={8} lg={4} key={link.path}>
            <Card
              hoverable
              style={{ textAlign: 'center' }}
              onClick={() => navigate(link.path)}
            >
              <Space direction="vertical" size="small">
                <span style={{ fontSize: 24, color: '#1890ff' }}>{link.icon}</span>
                <Text strong>{link.title}</Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
