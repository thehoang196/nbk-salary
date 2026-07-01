import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Button, Space, DatePicker, Select, message, Typography, Divider, Row, Col, Spin,
} from 'antd';
import {
  DownloadOutlined, FilePdfOutlined, FileExcelOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

/**
 * Trigger a browser file download from a blob response.
 * @param {Blob} blob - The file data
 * @param {string} filename - Suggested filename for download
 */
function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export default function BaoCao() {
  // State
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [employees, setEmployees] = useState([]);
  const [selectedNvId, setSelectedNvId] = useState(null);
  const [loadingEmployees, setLoadingEmployees] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingTongHop, setDownloadingTongHop] = useState(false);
  const [downloadingMisa, setDownloadingMisa] = useState(false);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch employee list for payslip selector
  const fetchEmployees = useCallback(async () => {
    setLoadingEmployees(true);
    try {
      const res = await api.get('/nhan-vien', { params: { trang_thai: 'dang_lam' } });
      setEmployees(res.data || []);
    } catch {
      message.error('Lỗi tải danh sách nhân viên');
      setEmployees([]);
    } finally {
      setLoadingEmployees(false);
    }
  }, []);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  // --- Download: Payslip PDF for individual employee ---
  const handleDownloadPayslipPdf = async () => {
    if (!selectedNvId) {
      message.warning('Vui lòng chọn nhân viên');
      return;
    }
    setDownloadingPdf(true);
    try {
      const res = await api.get(`/bao-cao/phieu-luong-pdf/${selectedNvId}/${thang}/${nam}`, {
        responseType: 'blob',
      });
      const employee = employees.find((e) => e.id === selectedNvId);
      const empName = employee?.ho_ten || selectedNvId;
      downloadBlob(res.data, `phieu_luong_${empName}_T${thang}_${nam}.html`);
      message.success('Tải phiếu lương thành công');
    } catch (err) {
      if (err.response?.status === 404) {
        message.error('Chưa có phiếu lương cho nhân viên này trong kỳ đã chọn');
      } else {
        message.error('Lỗi khi tải phiếu lương');
      }
    } finally {
      setDownloadingPdf(false);
    }
  };

  // --- Download: Monthly salary summary Excel ---
  const handleDownloadTongHop = async () => {
    setDownloadingTongHop(true);
    try {
      const res = await api.get(`/bao-cao/tong-hop/${thang}/${nam}`, {
        responseType: 'blob',
      });
      downloadBlob(res.data, `tong_hop_luong_T${thang}_${nam}.xlsx`);
      message.success('Tải báo cáo tổng hợp lương thành công');
    } catch (err) {
      if (err.response?.status === 404) {
        message.error('Chưa có dữ liệu lương cho kỳ đã chọn');
      } else {
        message.error('Lỗi khi tải báo cáo tổng hợp');
      }
    } finally {
      setDownloadingTongHop(false);
    }
  };

  // --- Download: Misa export Excel ---
  const handleDownloadMisa = async () => {
    setDownloadingMisa(true);
    try {
      const res = await api.get(`/bao-cao/export-misa/${thang}/${nam}`, {
        responseType: 'blob',
      });
      downloadBlob(res.data, `misa_luong_T${thang}_${nam}.xlsx`);
      message.success('Xuất file Misa thành công');
    } catch (err) {
      if (err.response?.status === 404) {
        message.error('Chưa có dữ liệu lương cho kỳ đã chọn');
      } else {
        message.error('Lỗi khi xuất file Misa');
      }
    } finally {
      setDownloadingMisa(false);
    }
  };

  return (
    <div>
      <Title level={4}>Báo cáo & Xuất dữ liệu</Title>

      {/* Period selector */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text strong>Kỳ báo cáo:</Text>
          <DatePicker
            picker="month"
            value={selectedMonth}
            onChange={(date) => date && setSelectedMonth(date)}
            format="MM/YYYY"
            allowClear={false}
          />
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Payslip PDF download section */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <FilePdfOutlined style={{ color: '#ff4d4f' }} />
                <span>Phiếu lương cá nhân</span>
              </Space>
            }
            size="small"
          >
            <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
              Tải phiếu lương (PDF/HTML) cho từng nhân viên theo tháng đã chọn.
            </Text>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Select
                showSearch
                placeholder="Chọn nhân viên"
                value={selectedNvId}
                onChange={setSelectedNvId}
                loading={loadingEmployees}
                style={{ width: '100%' }}
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().includes(input.toLowerCase())
                }
                notFoundContent={loadingEmployees ? <Spin size="small" /> : 'Không tìm thấy'}
              >
                {employees.map((nv) => (
                  <Option key={nv.id} value={nv.id}>
                    {nv.ho_ten} ({nv.ma_nv})
                  </Option>
                ))}
              </Select>
              <Button
                type="primary"
                danger
                icon={<FilePdfOutlined />}
                onClick={handleDownloadPayslipPdf}
                loading={downloadingPdf}
                disabled={!selectedNvId}
                block
              >
                Tải phiếu lương
              </Button>
            </Space>
          </Card>
        </Col>

        {/* Summary reports Excel download section */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <FileExcelOutlined style={{ color: '#52c41a' }} />
                <span>Báo cáo tổng hợp</span>
              </Space>
            }
            size="small"
          >
            <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
              Tải các báo cáo tổng hợp lương dạng Excel theo tháng đã chọn.
            </Text>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="primary"
                icon={<FileExcelOutlined />}
                onClick={handleDownloadTongHop}
                loading={downloadingTongHop}
                block
                style={{ background: '#52c41a', borderColor: '#52c41a' }}
              >
                Tải tổng hợp lương tháng
              </Button>
              <Divider style={{ margin: '8px 0' }} />
              <Button
                icon={<DownloadOutlined />}
                onClick={handleDownloadMisa}
                loading={downloadingMisa}
                block
              >
                Xuất Misa (Excel)
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
