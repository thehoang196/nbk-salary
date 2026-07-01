import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Tabs, Descriptions, Table, Modal, Form, Input, Button, Card,
  Statistic, Space, DatePicker, Select, Popconfirm, message, Spin, Tag, Row, Col,
} from 'antd';
import {
  ArrowLeftOutlined, PlusOutlined, DeleteOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';

// ============================================================================
// API helpers
// ============================================================================

const fetchEmployee = (id) => api.get(`/nhan-vien/${id}`);
const fetchContracts = (id) => api.get(`/nhan-vien/${id}/hop-dong`);
const fetchNghiepVuAssignments = (id) => api.get(`/nhan-vien/${id}/nghiep-vu`);
const fetchKiemNhiemAssignments = (id) => api.get(`/nhan-vien/${id}/kiem-nhiem`);
const fetchLuongKhoan = (id) => api.get(`/luong/luong-khoan/${id}`);
const fetchAllNghiepVu = () => api.get('/chuc-danh/nghiep-vu');
const fetchAllKiemNhiem = () => api.get('/chuc-danh/kiem-nhiem');

const assignNghiepVu = (nvId, data) => api.post(`/nhan-vien/${nvId}/nghiep-vu`, data);
const removeNghiepVu = (nvId, id) => api.delete(`/nhan-vien/${nvId}/nghiep-vu/${id}`);
const assignKiemNhiem = (nvId, data) => api.post(`/nhan-vien/${nvId}/kiem-nhiem`, data);
const removeKiemNhiem = (nvId, id) => api.delete(`/nhan-vien/${nvId}/kiem-nhiem/${id}`);

const createContract = (nvId, data) => api.post(`/nhan-vien/${nvId}/hop-dong`, data);

// ============================================================================
// Thông tin tab
// ============================================================================

function ThongTinTab({ employee }) {
  if (!employee) return null;

  const nhomLabel = employee.nhom_nv === 'GV' ? 'Giáo viên' : 'Văn phòng';
  const trangThaiMap = {
    dang_lam: { color: 'green', text: 'Đang làm' },
    nghi_viec: { color: 'red', text: 'Nghỉ việc' },
    tam_nghi: { color: 'orange', text: 'Tạm nghỉ' },
  };
  const tt = trangThaiMap[employee.trang_thai] || { color: 'default', text: employee.trang_thai };

  return (
    <Descriptions bordered column={2} size="small">
      <Descriptions.Item label="Mã NV">{employee.ma_nv}</Descriptions.Item>
      <Descriptions.Item label="Họ tên">{employee.ho_ten}</Descriptions.Item>
      {employee.nhom_nv === 'GV' && (
        <Descriptions.Item label="Tên gọi">{employee.ten_goi || '—'}</Descriptions.Item>
      )}
      <Descriptions.Item label="Nhóm NV">
        <Tag color={employee.nhom_nv === 'GV' ? 'blue' : 'purple'}>{nhomLabel}</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="Trạng thái">
        <Tag color={tt.color}>{tt.text}</Tag>
      </Descriptions.Item>
      <Descriptions.Item label="CCCD">{employee.cccd || '—'}</Descriptions.Item>
      <Descriptions.Item label="Ngày sinh">
        {employee.ngay_sinh ? dayjs(employee.ngay_sinh).format('DD/MM/YYYY') : '—'}
      </Descriptions.Item>
      <Descriptions.Item label="Email">{employee.email || '—'}</Descriptions.Item>
      <Descriptions.Item label="SĐT">{employee.sdt || '—'}</Descriptions.Item>
      <Descriptions.Item label="Ngày vào làm">
        {employee.ngay_vao_lam ? dayjs(employee.ngay_vao_lam).format('DD/MM/YYYY') : '—'}
      </Descriptions.Item>
      <Descriptions.Item label="Loại hợp đồng">{employee.loai_hop_dong || '—'}</Descriptions.Item>
      <Descriptions.Item label="Số người phụ thuộc">{employee.so_nguoi_phu_thuoc ?? 0}</Descriptions.Item>
    </Descriptions>
  );
}

// ============================================================================
// Hợp đồng tab
// ============================================================================

function HopDongTab({ employeeId }) {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const loadContracts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchContracts(employeeId);
      setContracts(res.data);
    } catch {
      message.error('Lỗi tải danh sách hợp đồng');
    } finally {
      setLoading(false);
    }
  }, [employeeId]);

  useEffect(() => { loadContracts(); }, [loadContracts]);

  const handleCreate = async (values) => {
    try {
      const payload = {
        ...values,
        ngay_bat_dau: values.ngay_bat_dau.format('YYYY-MM-DD'),
        ngay_ket_thuc: values.ngay_ket_thuc ? values.ngay_ket_thuc.format('YYYY-MM-DD') : null,
      };
      await createContract(employeeId, payload);
      message.success('Thêm hợp đồng thành công');
      setModalOpen(false);
      form.resetFields();
      loadContracts();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi thêm hợp đồng');
    }
  };

  const columns = [
    { title: 'Loại', dataIndex: 'loai', key: 'loai' },
    {
      title: 'Lương đóng BH',
      dataIndex: 'luong_dong_bh',
      key: 'luong_dong_bh',
      render: (v) => v ? `${v.toLocaleString()} đ` : '—',
    },
    {
      title: 'Ngày bắt đầu',
      dataIndex: 'ngay_bat_dau',
      key: 'ngay_bat_dau',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Ngày kết thúc',
      dataIndex: 'ngay_ket_thuc',
      key: 'ngay_ket_thuc',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : 'Không xác định',
    },
    { title: 'Ghi chú', dataIndex: 'ghi_chu', key: 'ghi_chu', render: (v) => v || '—' },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalOpen(true); }}>
          Thêm hợp đồng
        </Button>
      </div>
      <Table dataSource={contracts} columns={columns} rowKey="id" loading={loading} size="small" />
      <Modal
        title="Thêm hợp đồng mới"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="loai" label="Loại hợp đồng" rules={[{ required: true, message: 'Chọn loại HĐ' }]}>
            <Select
              options={[
                { value: 'xac_dinh', label: 'Xác định thời hạn' },
                { value: 'khong_xac_dinh', label: 'Không xác định thời hạn' },
                { value: 'thu_viec', label: 'Thử việc' },
              ]}
            />
          </Form.Item>
          <Form.Item name="luong_dong_bh" label="Lương đóng BH (VND)">
            <Input type="number" min={0} />
          </Form.Item>
          <Form.Item name="ngay_bat_dau" label="Ngày bắt đầu" rules={[{ required: true, message: 'Chọn ngày' }]}>
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="ngay_ket_thuc" label="Ngày kết thúc">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="ghi_chu" label="Ghi chú">
            <Input.TextArea rows={2} maxLength={500} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

// ============================================================================
// Nghiệp vụ tab
// ============================================================================

function NghiepVuTab({ employeeId }) {
  const [assignments, setAssignments] = useState([]);
  const [allNghiepVu, setAllNghiepVu] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [assignRes, allRes] = await Promise.all([
        fetchNghiepVuAssignments(employeeId),
        fetchAllNghiepVu(),
      ]);
      setAssignments(assignRes.data);
      setAllNghiepVu(allRes.data);
    } catch {
      message.error('Lỗi tải dữ liệu nghiệp vụ');
    } finally {
      setLoading(false);
    }
  }, [employeeId]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleAssign = async (values) => {
    try {
      const payload = {
        nghiep_vu_id: values.nghiep_vu_id,
        mo_ta: values.mo_ta || null,
        ngay_bat_dau: values.ngay_bat_dau.format('YYYY-MM-DD'),
        ngay_ket_thuc: values.ngay_ket_thuc ? values.ngay_ket_thuc.format('YYYY-MM-DD') : null,
      };
      await assignNghiepVu(employeeId, payload);
      message.success('Phân công nghiệp vụ thành công');
      setModalOpen(false);
      form.resetFields();
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi phân công');
    }
  };

  const handleRemove = async (assignmentId) => {
    try {
      await removeNghiepVu(employeeId, assignmentId);
      message.success('Đã xóa phân công');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi xóa');
    }
  };

  // Build a lookup map for nghiep_vu names
  const nvNameMap = {};
  allNghiepVu.forEach((nv) => { nvNameMap[nv.id] = `${nv.ma} - ${nv.ten}`; });

  const columns = [
    {
      title: 'Nghiệp vụ',
      dataIndex: 'nghiep_vu_id',
      key: 'nghiep_vu_id',
      render: (id) => nvNameMap[id] || `ID: ${id}`,
    },
    { title: 'Mô tả', dataIndex: 'mo_ta', key: 'mo_ta', render: (v) => v || '—' },
    {
      title: 'Ngày bắt đầu',
      dataIndex: 'ngay_bat_dau',
      key: 'ngay_bat_dau',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Ngày kết thúc',
      dataIndex: 'ngay_ket_thuc',
      key: 'ngay_ket_thuc',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : 'Không xác định',
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Popconfirm title="Xác nhận xóa phân công?" onConfirm={() => handleRemove(record.id)}>
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalOpen(true); }}>
          Thêm nghiệp vụ
        </Button>
      </div>
      <Table dataSource={assignments} columns={columns} rowKey="id" loading={loading} size="small" />
      <Modal
        title="Phân công nghiệp vụ"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleAssign}>
          <Form.Item name="nghiep_vu_id" label="Nghiệp vụ" rules={[{ required: true, message: 'Chọn nghiệp vụ' }]}>
            <Select
              showSearch
              placeholder="Chọn nghiệp vụ"
              optionFilterProp="label"
              options={allNghiepVu
                .filter((nv) => nv.is_active)
                .map((nv) => ({ value: nv.id, label: `${nv.ma} - ${nv.ten}` }))}
            />
          </Form.Item>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} maxLength={255} placeholder="Mô tả (không tham gia tính lương)" />
          </Form.Item>
          <Form.Item name="ngay_bat_dau" label="Ngày bắt đầu" rules={[{ required: true, message: 'Chọn ngày' }]}>
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="ngay_ket_thuc" label="Ngày kết thúc">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

// ============================================================================
// Kiêm nhiệm tab
// ============================================================================

function KiemNhiemTab({ employeeId }) {
  const [assignments, setAssignments] = useState([]);
  const [allKiemNhiem, setAllKiemNhiem] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [assignRes, allRes] = await Promise.all([
        fetchKiemNhiemAssignments(employeeId),
        fetchAllKiemNhiem(),
      ]);
      setAssignments(assignRes.data);
      setAllKiemNhiem(allRes.data);
    } catch {
      message.error('Lỗi tải dữ liệu kiêm nhiệm');
    } finally {
      setLoading(false);
    }
  }, [employeeId]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleAssign = async (values) => {
    try {
      const payload = {
        kiem_nhiem_id: values.kiem_nhiem_id,
        mo_ta: values.mo_ta || null,
        ngay_bat_dau: values.ngay_bat_dau.format('YYYY-MM-DD'),
        ngay_ket_thuc: values.ngay_ket_thuc ? values.ngay_ket_thuc.format('YYYY-MM-DD') : null,
      };
      await assignKiemNhiem(employeeId, payload);
      message.success('Phân công kiêm nhiệm thành công');
      setModalOpen(false);
      form.resetFields();
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi phân công');
    }
  };

  const handleRemove = async (assignmentId) => {
    try {
      await removeKiemNhiem(employeeId, assignmentId);
      message.success('Đã xóa phân công');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi xóa');
    }
  };

  // Build lookup map
  const knNameMap = {};
  allKiemNhiem.forEach((kn) => { knNameMap[kn.id] = `${kn.ma} - ${kn.ten}`; });

  const columns = [
    {
      title: 'Kiêm nhiệm',
      dataIndex: 'kiem_nhiem_id',
      key: 'kiem_nhiem_id',
      render: (id) => knNameMap[id] || `ID: ${id}`,
    },
    { title: 'Mô tả', dataIndex: 'mo_ta', key: 'mo_ta', render: (v) => v || '—' },
    {
      title: 'Ngày bắt đầu',
      dataIndex: 'ngay_bat_dau',
      key: 'ngay_bat_dau',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : '—',
    },
    {
      title: 'Ngày kết thúc',
      dataIndex: 'ngay_ket_thuc',
      key: 'ngay_ket_thuc',
      render: (v) => v ? dayjs(v).format('DD/MM/YYYY') : 'Không xác định',
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Popconfirm title="Xác nhận xóa phân công?" onConfirm={() => handleRemove(record.id)}>
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setModalOpen(true); }}>
          Thêm kiêm nhiệm
        </Button>
      </div>
      <Table dataSource={assignments} columns={columns} rowKey="id" loading={loading} size="small" />
      <Modal
        title="Phân công kiêm nhiệm"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleAssign}>
          <Form.Item name="kiem_nhiem_id" label="Kiêm nhiệm" rules={[{ required: true, message: 'Chọn kiêm nhiệm' }]}>
            <Select
              showSearch
              placeholder="Chọn kiêm nhiệm"
              optionFilterProp="label"
              options={allKiemNhiem
                .filter((kn) => kn.is_active)
                .map((kn) => ({ value: kn.id, label: `${kn.ma} - ${kn.ten}` }))}
            />
          </Form.Item>
          <Form.Item name="mo_ta" label="Mô tả">
            <Input.TextArea rows={2} maxLength={255} placeholder="Mô tả (không tham gia tính lương)" />
          </Form.Item>
          <Form.Item name="ngay_bat_dau" label="Ngày bắt đầu" rules={[{ required: true, message: 'Chọn ngày' }]}>
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="ngay_ket_thuc" label="Ngày kết thúc">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

// ============================================================================
// Lương Khoán breakdown card
// ============================================================================

function LuongKhoanCard({ employeeId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadLuongKhoan = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchLuongKhoan(employeeId);
      setData(res.data);
    } catch {
      // Employee might not have full data yet
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [employeeId]);

  useEffect(() => { loadLuongKhoan(); }, [loadLuongKhoan]);

  if (loading) return <Spin />;
  if (!data) return <Card size="small"><p>Chưa có dữ liệu lương khoán</p></Card>;

  const formatVND = (v) => `${(v || 0).toLocaleString()} đ`;

  return (
    <Card title="Lương Khoán" size="small" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <div style={{ fontSize: 13, color: '#666', marginBottom: 8 }}>
            <strong>Công thức:</strong> đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (n × 2.000.000) + (m × 3.000.000)
          </div>
        </Col>
        <Col xs={12} sm={6}>
          <Statistic title="Đơn giá Chức vụ" value={data.chuc_vu_don_gia} formatter={(v) => formatVND(v)} />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic title="Đơn giá Cấp bậc" value={data.cap_bac_don_gia} formatter={(v) => formatVND(v)} />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title={`Nghiệp vụ (${data.nghiep_vu_count} × 2M)`}
            value={data.nghiep_vu_total}
            formatter={(v) => formatVND(v)}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title={`Kiêm nhiệm (${data.kiem_nhiem_count} × 3M)`}
            value={data.kiem_nhiem_total}
            formatter={(v) => formatVND(v)}
          />
        </Col>
        <Col span={24}>
          <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 12, marginTop: 8 }}>
            <Statistic
              title="Tổng Lương Khoán"
              value={data.tong_luong_khoan}
              formatter={(v) => formatVND(v)}
              valueStyle={{ color: '#1890ff', fontWeight: 'bold', fontSize: 20 }}
            />
            <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
              = {formatVND(data.chuc_vu_don_gia)} + {formatVND(data.cap_bac_don_gia)} + ({data.nghiep_vu_count} × 2.000.000) + ({data.kiem_nhiem_count} × 3.000.000) = {formatVND(data.tong_luong_khoan)}
            </div>
          </div>
        </Col>
      </Row>
    </Card>
  );
}

// ============================================================================
// Main NhanVienDetail page
// ============================================================================

export default function NhanVienDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadEmployee = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchEmployee(id);
      setEmployee(res.data);
    } catch {
      message.error('Không thể tải thông tin nhân viên');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadEmployee(); }, [loadEmployee]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!employee) {
    return <div>Không tìm thấy nhân viên</div>;
  }

  const tabItems = [
    {
      key: 'thong-tin',
      label: 'Thông tin',
      children: <ThongTinTab employee={employee} />,
    },
    {
      key: 'hop-dong',
      label: 'Hợp đồng',
      children: <HopDongTab employeeId={parseInt(id)} />,
    },
    {
      key: 'nghiep-vu',
      label: 'Nghiệp vụ',
      children: <NghiepVuTab employeeId={parseInt(id)} />,
    },
    {
      key: 'kiem-nhiem',
      label: 'Kiêm nhiệm',
      children: <KiemNhiemTab employeeId={parseInt(id)} />,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/nhan-vien')}>
          Quay lại
        </Button>
        <span style={{ marginLeft: 16, fontSize: 18, fontWeight: 600 }}>
          {employee.ho_ten} ({employee.ma_nv})
        </span>
      </div>

      <LuongKhoanCard employeeId={parseInt(id)} />

      <Card size="small">
        <Tabs items={tabItems} defaultActiveKey="thong-tin" />
      </Card>
    </div>
  );
}
