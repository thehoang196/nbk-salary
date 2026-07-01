import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, DatePicker, message, Modal, Tag, Card, Typography,
} from 'antd';
import {
  CalculatorOutlined, CheckCircleOutlined, EyeOutlined, DownloadOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import useAuthStore from '../store/authStore';

const { Title } = Typography;
const { confirm } = Modal;

// Status color mapping
const STATUS_CONFIG = {
  draft: { color: 'default', label: 'Nháp' },
  reviewed: { color: 'blue', label: 'Đã duyệt' },
  approved: { color: 'green', label: 'Đã phê duyệt' },
};

export default function BangLuong() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const userRole = user?.role;

  // State
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [exporting, setExporting] = useState(false);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch salary table data
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/luong/bang-luong/${thang}/${nam}`);
      setData(res.data || []);
    } catch (e) {
      if (e.response?.status !== 404) {
        message.error('Lỗi tải dữ liệu bảng lương');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Month change handler
  const handleMonthChange = (date) => {
    if (date) setSelectedMonth(date);
  };

  // Calculate salary for all employees
  const handleTinhLuong = () => {
    confirm({
      title: 'Xác nhận tính lương',
      content: `Bạn có chắc chắn muốn tính lương cho tất cả nhân viên tháng ${thang}/${nam}? Quá trình này sẽ tính toán lại toàn bộ bảng lương.`,
      okText: 'Tính lương',
      cancelText: 'Hủy',
      okType: 'primary',
      icon: <CalculatorOutlined style={{ color: '#1677ff' }} />,
      onOk: async () => {
        setCalculating(true);
        try {
          const res = await api.post('/luong/tinh-luong', { thang, nam });
          const count = res.data?.count || res.data?.length || 0;
          message.success(`Đã tính lương thành công cho ${count} nhân viên`);
          fetchData();
        } catch (e) {
          const detail = e.response?.data?.detail;
          if (typeof detail === 'string') {
            message.error(detail);
          } else if (Array.isArray(detail)) {
            message.error(`Lỗi tính lương: ${detail.map((d) => d.msg || d).join(', ')}`);
          } else {
            message.error('Lỗi khi tính lương. Vui lòng kiểm tra dữ liệu đầu vào.');
          }
        } finally {
          setCalculating(false);
        }
      },
    });
  };

  // Export salary data to Misa-compatible Excel format
  const handleExportMisa = async () => {
    setExporting(true);
    try {
      const response = await api.post('/export/misa', { thang, nam }, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `misa_luong_${thang}_${nam}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      message.success('Xuất file Misa thành công');
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (typeof detail === 'string') {
        message.error(detail);
      } else {
        message.error('Lỗi khi xuất file Misa. Vui lòng thử lại.');
      }
    } finally {
      setExporting(false);
    }
  };

  // Approve salary record: Draft → "Duyệt" (Accountant/Admin) → Reviewed → "Phê duyệt" (Admin) → Approved
  const handleDuyet = async (record) => {
    const nextStatus = record.trang_thai === 'draft' ? 'reviewed' : 'approved';
    const nextLabel = nextStatus === 'reviewed' ? 'Duyệt' : 'Phê duyệt';

    confirm({
      title: `${nextLabel} bảng lương`,
      content: `Bạn có chắc chắn muốn ${nextLabel.toLowerCase()} bảng lương của ${record.ho_ten || record.nhan_vien_name}?`,
      okText: nextLabel,
      cancelText: 'Hủy',
      onOk: async () => {
        try {
          await api.put(`/luong/duyet/${record.id}`, {
            version: record.version,
            trang_thai_moi: nextStatus,
          });
          message.success(`${nextLabel} thành công`);
          fetchData();
        } catch (e) {
          const detail = e.response?.data?.detail;
          if (e.response?.status === 409) {
            // Conflict detected: version changed since load (Req 13.2, 13.3)
            const currentData = e.response?.data?.current;
            Modal.warning({
              title: 'Xung đột dữ liệu',
              content: (
                <div>
                  <p>Bản ghi đã bị thay đổi bởi người dùng khác kể từ khi bạn tải dữ liệu.</p>
                  {currentData && (
                    <div style={{ marginTop: 8, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                      <p style={{ marginBottom: 4 }}><strong>Dữ liệu hiện tại trên hệ thống:</strong></p>
                      {currentData.trang_thai && (
                        <p style={{ margin: 0 }}>Trạng thái: {STATUS_CONFIG[currentData.trang_thai]?.label || currentData.trang_thai}</p>
                      )}
                      {currentData.nguoi_duyet && (
                        <p style={{ margin: 0 }}>Người duyệt: {currentData.nguoi_duyet}</p>
                      )}
                      {currentData.ngay_duyet && (
                        <p style={{ margin: 0 }}>Ngày duyệt: {dayjs(currentData.ngay_duyet).format('DD/MM/YYYY HH:mm')}</p>
                      )}
                      {currentData.version && (
                        <p style={{ margin: 0 }}>Phiên bản: {currentData.version}</p>
                      )}
                    </div>
                  )}
                  <p style={{ marginTop: 8 }}>Vui lòng tải lại dữ liệu và thực hiện lại thao tác.</p>
                </div>
              ),
              okText: 'Tải lại dữ liệu',
              onOk: () => fetchData(),
            });
          } else {
            message.error(detail || `Lỗi khi ${nextLabel.toLowerCase()}`);
          }
        }
      },
    });
  };

  // Navigate to payslip detail
  const handleViewPayslip = (record) => {
    const nvId = record.nhan_vien_id;
    navigate(`/phieu-luong/${nvId}/${thang}/${nam}`);
  };

  // Determine if user can approve based on role
  const canApprove = (status) => {
    if (userRole === 'admin') return status !== 'approved';
    if (userRole === 'accountant') return status === 'draft';
    return false;
  };

  // Determine if user can calculate
  const canCalculate = userRole === 'admin' || userRole === 'accountant';

  // Table columns
  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Nhân viên',
      dataIndex: 'ho_ten',
      key: 'ho_ten',
      render: (text, record) => text || record.nhan_vien_name || `NV #${record.nhan_vien_id}`,
      sorter: (a, b) => (a.ho_ten || '').localeCompare(b.ho_ten || ''),
    },
    {
      title: 'Lương khoán',
      dataIndex: 'luong_khoan',
      key: 'luong_khoan',
      align: 'right',
      render: (val) => (val || 0).toLocaleString('vi-VN'),
      sorter: (a, b) => (a.luong_khoan || 0) - (b.luong_khoan || 0),
    },
    {
      title: 'Thu nhập dạy',
      dataIndex: 'thu_nhap_day',
      key: 'thu_nhap_day',
      align: 'right',
      render: (val) => (val || 0).toLocaleString('vi-VN'),
      sorter: (a, b) => (a.thu_nhap_day || 0) - (b.thu_nhap_day || 0),
    },
    {
      title: 'Hỗ trợ',
      dataIndex: 'ho_tro',
      key: 'ho_tro',
      align: 'right',
      render: (val) => (val || 0).toLocaleString('vi-VN'),
    },
    {
      title: 'Tổng thu',
      dataIndex: 'tong_thu',
      key: 'tong_thu',
      align: 'right',
      render: (val) => (
        <strong>{(val || 0).toLocaleString('vi-VN')}</strong>
      ),
      sorter: (a, b) => (a.tong_thu || 0) - (b.tong_thu || 0),
    },
    {
      title: 'Khấu trừ',
      dataIndex: 'khau_tru',
      key: 'khau_tru',
      align: 'right',
      render: (val) => (val || 0).toLocaleString('vi-VN'),
    },
    {
      title: 'Thực lĩnh',
      dataIndex: 'thuc_linh',
      key: 'thuc_linh',
      align: 'right',
      render: (val) => (
        <strong style={{ color: '#1677ff' }}>
          {(val || 0).toLocaleString('vi-VN')}
        </strong>
      ),
      sorter: (a, b) => (a.thuc_linh || 0) - (b.thuc_linh || 0),
    },
    {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      key: 'trang_thai',
      width: 110,
      align: 'center',
      render: (status) => {
        const config = STATUS_CONFIG[status] || STATUS_CONFIG.draft;
        return <Tag color={config.color}>{config.label}</Tag>;
      },
      filters: Object.entries(STATUS_CONFIG).map(([key, cfg]) => ({
        text: cfg.label,
        value: key,
      })),
      onFilter: (value, record) => record.trang_thai === value,
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 130,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewPayslip(record)}
            title="Xem phiếu lương"
          />
          {canApprove(record.trang_thai) && (
            <Button
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => handleDuyet(record)}
              title={record.trang_thai === 'draft' ? 'Duyệt' : 'Phê duyệt'}
            />
          )}
        </Space>
      ),
    },
  ];

  // Summary row
  const summary = (pageData) => {
    let totalTongThu = 0;
    let totalKhauTru = 0;
    let totalThucLinh = 0;

    pageData.forEach((row) => {
      totalTongThu += row.tong_thu || 0;
      totalKhauTru += row.khau_tru || 0;
      totalThucLinh += row.thuc_linh || 0;
    });

    return (
      <Table.Summary.Row>
        <Table.Summary.Cell index={0} colSpan={5} align="right">
          <strong>Tổng cộng:</strong>
        </Table.Summary.Cell>
        <Table.Summary.Cell index={5} align="right">
          <strong>{totalTongThu.toLocaleString('vi-VN')}</strong>
        </Table.Summary.Cell>
        <Table.Summary.Cell index={6} align="right">
          <strong>{totalKhauTru.toLocaleString('vi-VN')}</strong>
        </Table.Summary.Cell>
        <Table.Summary.Cell index={7} align="right">
          <strong style={{ color: '#1677ff' }}>
            {totalThucLinh.toLocaleString('vi-VN')}
          </strong>
        </Table.Summary.Cell>
        <Table.Summary.Cell index={8} colSpan={2} />
      </Table.Summary.Row>
    );
  };

  return (
    <div>
      <Title level={4}>Bảng lương</Title>

      {/* Month/Year selector + Action buttons */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <span>Tháng:</span>
          <DatePicker
            picker="month"
            value={selectedMonth}
            onChange={handleMonthChange}
            format="MM/YYYY"
            allowClear={false}
          />
          {canCalculate && (
            <Button
              type="primary"
              icon={<CalculatorOutlined />}
              onClick={handleTinhLuong}
              loading={calculating}
            >
              Tính lương
            </Button>
          )}
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExportMisa}
            loading={exporting}
          >
            Xuất Misa
          </Button>
        </Space>
      </Card>

      {/* Salary summary table */}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (t) => `Tổng: ${t} nhân viên`,
        }}
        size="small"
        bordered
        scroll={{ x: 1100 }}
        summary={summary}
        onRow={(record) => ({
          style: { cursor: 'pointer' },
          onDoubleClick: () => handleViewPayslip(record),
        })}
      />
    </div>
  );
}
