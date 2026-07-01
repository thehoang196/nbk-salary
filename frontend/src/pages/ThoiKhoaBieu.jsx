import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table, Button, Space, DatePicker, message, Modal, Tag, Typography, Card, Statistic, Row, Col,
} from 'antd';
import {
  UploadOutlined, DownloadOutlined, FileSearchOutlined,
  HistoryOutlined, BarChartOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Title, Text } = Typography;

const LOAI_TIET_LABELS = {
  chinh_khoa: 'Chính khóa',
  tnst_vy: 'TNST VY',
  k9_luyen_thi: 'K9 Luyện thi',
  kh_ta: 'KH bằng TA',
  ielts: 'IELTS',
};

const LOAI_TIET_COLORS = {
  chinh_khoa: 'blue',
  tnst_vy: 'green',
  k9_luyen_thi: 'orange',
  kh_ta: 'purple',
  ielts: 'cyan',
};

export default function ThoiKhoaBieu() {
  const navigate = useNavigate();

  // State
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [importSummary, setImportSummary] = useState(null);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch TKB data for selected month/year
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/tkb/${thang}/${nam}`);
      setData(res.data);
    } catch (e) {
      if (e.response?.status !== 404) {
        message.error('Lỗi tải dữ liệu thời khóa biểu');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle month change
  const handleMonthChange = (date) => {
    if (date) {
      setSelectedMonth(date);
      setImportSummary(null);
    }
  };

  // Handle import confirm — this is called by ImportExcel component
  const handleImportConfirm = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thang', thang);
    formData.append('nam', nam);

    try {
      const res = await api.post('/tkb/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const result = res.data;
      setImportSummary(result);
      fetchData();
      return result;
    } catch (e) {
      if (e.response?.status === 409) {
        // Month already has data — ask user to confirm replace
        return new Promise((resolve, reject) => {
          Modal.confirm({
            title: 'Dữ liệu đã tồn tại',
            content: (
              <div>
                <p>Dữ liệu TKB tháng {thang}/{nam} đã tồn tại trong hệ thống.</p>
                <p>Bạn có muốn <strong>ghi đè</strong> dữ liệu cũ không?</p>
              </div>
            ),
            okText: 'Ghi đè',
            okType: 'danger',
            cancelText: 'Hủy',
            onOk: async () => {
              try {
                const formData2 = new FormData();
                formData2.append('file', file);
                formData2.append('thang', thang);
                formData2.append('nam', nam);
                formData2.append('replace_existing', 'true');

                const res2 = await api.post('/tkb/import', formData2, {
                  headers: { 'Content-Type': 'multipart/form-data' },
                });
                const result2 = res2.data;
                setImportSummary(result2);
                fetchData();
                resolve(result2);
              } catch (err) {
                reject(err);
              }
            },
            onCancel: () => {
              reject({ cancelled: true });
            },
          });
        });
      }
      throw e;
    }
  };

  // Template download handler (calls API with auth token, then generates CSV)
  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/tkb/template');
      const templateInfo = response.data;
      const columns = templateInfo.columns.map((c) => c.name);
      const descriptions = templateInfo.columns.map((c) => c.description);
      const csvContent = columns.join(',') + '\n' + descriptions.join(',') + '\n';
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'mau_tkb_import.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      message.error('Không thể tải file mẫu');
    }
  };

  // Template download URL (for ImportExcel component)
  const templateUrl = `${api.defaults.baseURL}/tkb/template`;

  // Table columns
  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 60,
      align: 'center',
      render: (_, __, idx) => idx + 1,
    },
    {
      title: 'Giáo viên',
      dataIndex: 'nhan_vien_ho_ten',
      key: 'nhan_vien_ho_ten',
      width: 180,
      render: (val, record) => val || `NV #${record.nhan_vien_id}`,
    },
    {
      title: 'Môn học',
      dataIndex: 'mon_hoc_ten',
      key: 'mon_hoc_ten',
      width: 150,
      render: (val, record) => val || `MH #${record.mon_hoc_id}`,
    },
    {
      title: 'Khối',
      dataIndex: 'khoi_ten',
      key: 'khoi_ten',
      width: 100,
      render: (val, record) => val || `K #${record.khoi_id}`,
    },
    {
      title: 'Lớp',
      dataIndex: 'lop_ten',
      key: 'lop_ten',
      width: 100,
      render: (val, record) => val || `L #${record.lop_id}`,
    },
    {
      title: 'Số tiết',
      dataIndex: 'so_tiet',
      key: 'so_tiet',
      width: 90,
      align: 'center',
    },
    {
      title: 'Loại tiết',
      dataIndex: 'loai_tiet',
      key: 'loai_tiet',
      width: 130,
      render: (val) => (
        <Tag color={LOAI_TIET_COLORS[val] || 'default'}>
          {LOAI_TIET_LABELS[val] || val}
        </Tag>
      ),
    },
  ];

  // Calculate summary statistics
  const totalRecords = data.length;
  const totalPeriods = data.reduce((sum, r) => sum + (r.so_tiet || 0), 0);
  const uniqueTeachers = new Set(data.map((r) => r.nhan_vien_id)).size;

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Thời khóa biểu</Title>
        <Space>
          <Button
            icon={<BarChartOutlined />}
            onClick={() => navigate('/bcc')}
          >
            BCC Tổng tiết
          </Button>
          <Button
            icon={<HistoryOutlined />}
            onClick={() => navigate('/tkb/thay-doi')}
          >
            Nhật ký thay đổi
          </Button>
        </Space>
      </div>

      {/* Month selector + Import button */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Text strong>Tháng/Năm:</Text>
            <DatePicker
              picker="month"
              value={selectedMonth}
              onChange={handleMonthChange}
              format="MM/YYYY"
              allowClear={false}
              style={{ width: 150 }}
            />
          </Space>
        </Col>
        <Col flex="auto" style={{ textAlign: 'right' }}>
          <Space>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleDownloadTemplate}
            >
              Tải mẫu import
            </Button>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setImportOpen(true)}
            >
              Import TKB
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Summary statistics */}
      {data.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Tổng bản ghi" value={totalRecords} />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Tổng số tiết" value={totalPeriods} />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Số giáo viên" value={uniqueTeachers} />
            </Card>
          </Col>
        </Row>
      )}

      {/* Import summary after successful import */}
      {importSummary && (
        <Card
          size="small"
          style={{ marginBottom: 16, borderColor: '#52c41a' }}
          title={
            <Space>
              <FileSearchOutlined style={{ color: '#52c41a' }} />
              <Text strong>Kết quả import</Text>
            </Space>
          }
        >
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="Đã import"
                value={importSummary.imported_count}
                suffix="dòng"
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Tổng dòng"
                value={importSummary.total_rows}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Lỗi"
                value={importSummary.errors?.length || 0}
                valueStyle={importSummary.errors?.length > 0 ? { color: '#cf1322' } : undefined}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* Data table */}
      <Table
        dataSource={data}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        scroll={{ x: 900 }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100'],
          showTotal: (total) => `Tổng ${total} bản ghi`,
        }}
        locale={{ emptyText: `Không có dữ liệu TKB tháng ${thang}/${nam}` }}
      />

      {/* Import modal */}
      <ImportExcel
        title={`Import TKB tháng ${thang}/${nam}`}
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleImportConfirm}
        accept=".xlsx,.xls,.csv"
        maxSize={10}
        templateUrl={templateUrl}
      />
    </div>
  );
}
