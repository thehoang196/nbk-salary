import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Table,
  Statistic,
  Button,
  Tag,
  Space,
  Divider,
  Spin,
  Alert,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
} from '@ant-design/icons';
import api from '../services/api';

const formatVND = (value) => {
  if (value == null) return '0';
  return Number(value).toLocaleString('vi-VN');
};

export default function PhieuLuong() {
  const { nvId, thang, nam } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(null);

  useEffect(() => {
    fetchPhieuLuong();
  }, [nvId, thang, nam]);

  const fetchPhieuLuong = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/luong/phieu-luong/${nvId}/${thang}/${nam}`);
      setData(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Không thể tải phiếu lương. Vui lòng thử lại.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(format);
    try {
      const res = await api.post(
        `/export/phieu-luong/${nvId}/${thang}/${nam}?format=${format}`,
        null,
        { responseType: 'blob' }
      );
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const ext = format === 'pdf' ? 'pdf' : 'xlsx';
      link.download = `phieu_luong_${nvId}_${thang}_${nam}.${ext}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success(`Xuất ${format.toUpperCase()} thành công`);
    } catch {
      message.error(`Xuất ${format.toUpperCase()} thất bại`);
    } finally {
      setExporting(null);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" tip="Đang tải phiếu lương..." />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/bang-luong')}
          style={{ marginBottom: 16 }}
        >
          Quay lại bảng lương
        </Button>
        <Alert type="error" message="Lỗi" description={error} showIcon />
      </div>
    );
  }

  const { muc_i, muc_ii, muc_iii, muc_iv, muc_v, muc_vi } = data;

  // Section II income items for table
  const incomeItems = [
    { key: '1', stt: 1, ten: 'Lương khoán (theo ngày công)', so_tien: muc_ii.luong_khoan_thang },
    { key: '2', stt: 2, ten: 'Thu nhập dạy', so_tien: muc_ii.thu_nhap_day },
    { key: '3', stt: 3, ten: 'Thi, học sinh giỏi', so_tien: muc_ii.thi_hoc_sinh_gioi },
    { key: '4', stt: 4, ten: 'Hỗ trợ lương', so_tien: muc_ii.ho_tro_luong },
    { key: '5', stt: 5, ten: 'Sinh nhật', so_tien: muc_ii.sinh_nhat },
    { key: '6', stt: 6, ten: 'Làm thêm', so_tien: muc_ii.lam_them },
    { key: '7', stt: 7, ten: 'Sự kiện', so_tien: muc_ii.su_kien },
    { key: '8', stt: 8, ten: 'Phụ cấp', so_tien: muc_ii.phu_cap },
    { key: '9', stt: 9, ten: 'Tết', so_tien: muc_ii.tet },
  ];

  const incomeColumns = [
    { title: 'STT', dataIndex: 'stt', width: 60, align: 'center' },
    { title: 'Khoản thu nhập', dataIndex: 'ten' },
    {
      title: 'Số tiền (VNĐ)',
      dataIndex: 'so_tien',
      align: 'right',
      render: (val) => formatVND(val),
    },
  ];

  // Section IV deduction items for table
  const deductionItems = [
    { key: '1', stt: 1, ten: 'Bảo hiểm + Công đoàn (BH+CĐ)', so_tien: muc_iv.bao_hiem },
    { key: '2', stt: 2, ten: 'Đoàn phí', so_tien: muc_iv.doan_phi },
    { key: '3', stt: 3, ten: 'Tích lũy', so_tien: muc_iv.tich_luy },
    { key: '4', stt: 4, ten: 'Thuế TNCN', so_tien: muc_iv.thue_tncn },
    { key: '5', stt: 5, ten: 'Thu hồi', so_tien: muc_iv.thu_hoi },
  ];

  const deductionColumns = [
    { title: 'STT', dataIndex: 'stt', width: 60, align: 'center' },
    { title: 'Khoản khấu trừ', dataIndex: 'ten' },
    {
      title: 'Số tiền (VNĐ)',
      dataIndex: 'so_tien',
      align: 'right',
      render: (val) => formatVND(val),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <Space style={{ marginBottom: 16 }} size="middle">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/bang-luong')}
        >
          Quay lại bảng lương
        </Button>
        <Button
          icon={<FilePdfOutlined />}
          type="primary"
          danger
          loading={exporting === 'pdf'}
          onClick={() => handleExport('pdf')}
        >
          Xuất PDF
        </Button>
        <Button
          icon={<FileExcelOutlined />}
          type="primary"
          style={{ background: '#52c41a', borderColor: '#52c41a' }}
          loading={exporting === 'xlsx'}
          onClick={() => handleExport('xlsx')}
        >
          Xuất Excel
        </Button>
      </Space>

      <Card
        title={`PHIẾU LƯƠNG THÁNG ${thang}/${nam}`}
        style={{ maxWidth: 900, margin: '0 auto' }}
      >
        {/* Section I: Employee Info */}
        <Divider orientation="left">I. Thông tin nhân viên</Divider>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="Họ tên">{muc_i.ho_ten}</Descriptions.Item>
          <Descriptions.Item label="Tên gọi">
            {muc_i.ten_goi || '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Chức vụ">
            {muc_i.chuc_vu || '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Cấp bậc QL">
            {muc_i.cap_bac_ql || '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Nghiệp vụ" span={2}>
            {muc_i.nghiep_vu && muc_i.nghiep_vu.length > 0
              ? muc_i.nghiep_vu.map((nv) => (
                  <Tag color="blue" key={nv}>
                    {nv}
                  </Tag>
                ))
              : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Kiêm nhiệm" span={2}>
            {muc_i.kiem_nhiem && muc_i.kiem_nhiem.length > 0
              ? muc_i.kiem_nhiem.map((kn) => (
                  <Tag color="green" key={kn}>
                    {kn}
                  </Tag>
                ))
              : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="Lương khoán">
            <strong>{formatVND(muc_i.luong_khoan)} VNĐ</strong>
          </Descriptions.Item>
          <Descriptions.Item label="Ngày công">
            {muc_i.ngay_cong ?? '—'}
          </Descriptions.Item>
        </Descriptions>

        {/* Section II: Total Income */}
        <Divider orientation="left">II. Tổng thu nhập</Divider>
        <Table
          dataSource={incomeItems}
          columns={incomeColumns}
          pagination={false}
          size="small"
          bordered
          summary={() => (
            <Table.Summary.Row>
              <Table.Summary.Cell colSpan={2} align="right">
                <strong>Tổng cộng</strong>
              </Table.Summary.Cell>
              <Table.Summary.Cell align="right">
                <strong>{formatVND(muc_ii.tong)}</strong>
              </Table.Summary.Cell>
            </Table.Summary.Row>
          )}
        />

        {/* Section III: Already Received */}
        <Divider orientation="left">III. Đã nhận</Divider>
        <Descriptions bordered column={1} size="small">
          <Descriptions.Item label="Số tiền đã nhận trước">
            {formatVND(muc_iii.da_nhan)} VNĐ
          </Descriptions.Item>
        </Descriptions>

        {/* Section IV: Deductions */}
        <Divider orientation="left">IV. Các khoản khấu trừ</Divider>
        <Table
          dataSource={deductionItems}
          columns={deductionColumns}
          pagination={false}
          size="small"
          bordered
          summary={() => (
            <Table.Summary.Row>
              <Table.Summary.Cell colSpan={2} align="right">
                <strong>Tổng khấu trừ</strong>
              </Table.Summary.Cell>
              <Table.Summary.Cell align="right">
                <strong>{formatVND(muc_iv.tong)}</strong>
              </Table.Summary.Cell>
            </Table.Summary.Row>
          )}
        />

        {/* Section V: Tax Settlement */}
        {muc_v && muc_v.quyet_toan != null && muc_v.quyet_toan !== 0 && (
          <>
            <Divider orientation="left">V. Quyết toán thuế</Divider>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Quyết toán thuế TNCN">
                <span
                  style={{
                    color: muc_v.quyet_toan >= 0 ? '#52c41a' : '#ff4d4f',
                    fontWeight: 'bold',
                  }}
                >
                  {muc_v.quyet_toan >= 0 ? '+' : ''}
                  {formatVND(muc_v.quyet_toan)} VNĐ
                </span>
              </Descriptions.Item>
            </Descriptions>
          </>
        )}

        {/* Section VI: Net Pay (Highlighted) */}
        <Divider orientation="left">VI. Thực lĩnh</Divider>
        <div
          style={{
            textAlign: 'center',
            padding: '24px 0',
            background: '#f6ffed',
            borderRadius: 8,
            border: '2px solid #52c41a',
          }}
        >
          <Statistic
            title="SỐ TIỀN THỰC LĨNH"
            value={muc_vi.thuc_linh}
            precision={0}
            suffix="VNĐ"
            valueStyle={{
              color: '#389e0d',
              fontSize: 32,
              fontWeight: 'bold',
            }}
            formatter={(val) => formatVND(val)}
          />
        </div>
      </Card>
    </div>
  );
}
