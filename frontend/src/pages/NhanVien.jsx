import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table, Button, Space, Input, Select, Tag, Drawer, Form,
  InputNumber, message, Popconfirm, Row, Col,
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  SearchOutlined, EyeOutlined, UploadOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Option } = Select;

const NHOM_NV_OPTIONS = [
  { value: 'GV', label: 'Giáo viên' },
  { value: 'VP', label: 'Văn phòng' },
];

const TRANG_THAI_OPTIONS = [
  { value: 'dang_lam', label: 'Đang làm' },
  { value: 'nghi_viec', label: 'Nghỉ việc' },
  { value: 'thu_viec', label: 'Thử việc' },
];

const TRANG_THAI_COLORS = {
  dang_lam: 'green',
  nghi_viec: 'red',
  thu_viec: 'orange',
  tam_ngung: 'default',
};

const TRANG_THAI_LABELS = {
  dang_lam: 'Đang làm',
  nghi_viec: 'Nghỉ việc',
  thu_viec: 'Thử việc',
  tam_ngung: 'Tạm ngưng',
};

const formatVND = (value) => {
  if (value == null) return '—';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(value);
};

export default function NhanVien() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();

  // Filter state
  const [filters, setFilters] = useState({
    nhom_nv: undefined,
    trang_thai: undefined,
    don_vi_id: undefined,
    search: '',
  });

  // Import Excel state
  const [importOpen, setImportOpen] = useState(false);

  // Dropdown data for selects
  const [donViList, setDonViList] = useState([]);
  const [chucVuList, setChucVuList] = useState([]);
  const [capBacList, setCapBacList] = useState([]);

  // Watch nhom_nv in form for conditional rendering
  const formNhomNv = Form.useWatch('nhom_nv', form);

  const fetchEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.nhom_nv) params.nhom_nv = filters.nhom_nv;
      if (filters.trang_thai) params.trang_thai = filters.trang_thai;
      if (filters.don_vi_id) params.don_vi_id = filters.don_vi_id;
      if (filters.search) params.search = filters.search;

      const res = await api.get('/nhan-vien', { params });
      setData(res.data);
    } catch (e) {
      message.error('Lỗi tải danh sách nhân viên');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const fetchDropdowns = async () => {
    try {
      const [donViRes, chucVuRes, capBacRes] = await Promise.all([
        api.get('/danh-muc/don-vi'),
        api.get('/chuc-danh/chuc-vu'),
        api.get('/chuc-danh/cap-bac-ql'),
      ]);
      setDonViList(donViRes.data);
      setChucVuList(chucVuRes.data);
      setCapBacList(capBacRes.data);
    } catch (e) {
      // Silent fail for dropdowns
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  useEffect(() => {
    fetchDropdowns();
  }, []);

  const handleAdd = () => {
    setEditingRecord(null);
    form.resetFields();
    form.setFieldsValue({ trang_thai: 'dang_lam', nhom_nv: 'GV' });
    setDrawerOpen(true);
  };

  const handleEdit = (record) => {
    setEditingRecord(record);
    form.setFieldsValue({
      ma_nv: record.ma_nv,
      ho_ten: record.ho_ten,
      ten_goi: record.ten_goi,
      nhom_nv: record.nhom_nv,
      don_vi_id: record.don_vi_id,
      chuc_vu_id: record.chuc_vu_id,
      cap_bac_ql_id: record.cap_bac_ql_id,
      trang_thai: record.trang_thai,
      email: record.email,
      sdt: record.sdt,
    });
    setDrawerOpen(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/nhan-vien/${id}`);
      message.success('Đã xóa nhân viên');
      fetchEmployees();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Không thể xóa');
    }
  };

  const handleSubmit = async (values) => {
    try {
      // Clear ten_goi for VP
      if (values.nhom_nv === 'VP') {
        values.ten_goi = null;
      }

      if (editingRecord) {
        await api.put(`/nhan-vien/${editingRecord.id}`, values);
        message.success('Cập nhật thành công');
      } else {
        await api.post('/nhan-vien', values);
        message.success('Thêm nhân viên thành công');
      }
      setDrawerOpen(false);
      form.resetFields();
      setEditingRecord(null);
      fetchEmployees();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi thao tác');
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  // Import Excel handler - parse Excel client-side and send JSON to backend
  const handleImportConfirm = async (file) => {
    const XLSX = await import('xlsx');
    const arrayBuffer = await file.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const jsonData = XLSX.utils.sheet_to_json(sheet, { defval: '' });

    // Map Excel columns to API fields
    const rows = jsonData.map((row) => ({
      ma_nv: String(row['Mã NV'] || row['ma_nv'] || '').trim(),
      ho_ten: String(row['Họ tên'] || row['ho_ten'] || '').trim(),
      nhom_nv: String(row['Nhóm NV'] || row['nhom_nv'] || 'GV').trim(),
      don_vi: String(row['Đơn vị'] || row['don_vi'] || '').trim() || null,
      chuc_vu: String(row['Chức vụ'] || row['chuc_vu'] || '').trim() || null,
      cap_bac_ql: String(row['Cấp bậc QL'] || row['cap_bac_ql'] || '').trim() || null,
      ten_goi: String(row['Tên gọi'] || row['ten_goi'] || '').trim() || null,
      email: String(row['Email'] || row['email'] || '').trim() || null,
      sdt: String(row['SĐT'] || row['sdt'] || '').trim() || null,
    }));

    const res = await api.post('/nhan-vien/import', { rows });
    if (res.data.imported_count > 0) {
      fetchEmployees();
    }
    return res.data;
  };

  // Resolve names from IDs for display
  const getChucVuName = (record) => {
    if (record.chuc_vu?.ten) return record.chuc_vu.ten;
    if (record.chuc_vu_id) {
      const found = chucVuList.find((c) => c.id === record.chuc_vu_id);
      return found?.ten || '';
    }
    return '';
  };

  const getCapBacName = (record) => {
    if (record.cap_bac_ql?.ten) return record.cap_bac_ql.ten;
    if (record.cap_bac_ql_id) {
      const found = capBacList.find((c) => c.id === record.cap_bac_ql_id);
      return found?.ten || '';
    }
    return '';
  };

  const columns = [
    {
      title: 'Mã NV',
      dataIndex: 'ma_nv',
      key: 'ma_nv',
      width: 100,
    },
    {
      title: 'Họ tên',
      dataIndex: 'ho_ten',
      key: 'ho_ten',
      width: 180,
    },
    {
      title: 'Tên gọi',
      dataIndex: 'ten_goi',
      key: 'ten_goi',
      width: 120,
      render: (val, record) => (record.nhom_nv === 'GV' ? val || '—' : '—'),
    },
    {
      title: 'Nhóm',
      dataIndex: 'nhom_nv',
      key: 'nhom_nv',
      width: 80,
      render: (val) => (
        <Tag color={val === 'GV' ? 'blue' : 'purple'}>
          {val === 'GV' ? 'Giáo viên' : 'Văn phòng'}
        </Tag>
      ),
    },
    {
      title: 'Chức vụ',
      key: 'chuc_vu',
      width: 130,
      render: (_, record) => getChucVuName(record),
    },
    {
      title: 'Cấp bậc QL',
      key: 'cap_bac_ql',
      width: 130,
      render: (_, record) => getCapBacName(record),
    },
    {
      title: 'Lương khoán',
      dataIndex: 'luong_khoan',
      key: 'luong_khoan',
      width: 150,
      align: 'right',
      render: (val) => formatVND(val),
    },
    {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      key: 'trang_thai',
      width: 110,
      render: (val) => (
        <Tag color={TRANG_THAI_COLORS[val] || 'default'}>
          {TRANG_THAI_LABELS[val] || val}
        </Tag>
      ),
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 140,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/nhan-vien/${record.id}`)}
            title="Chi tiết"
          />
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            title="Sửa"
          />
          <Popconfirm
            title="Xác nhận xóa nhân viên này?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
          >
            <Button size="small" danger icon={<DeleteOutlined />} title="Xóa" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý nhân viên</h2>
        <Space>
          <Button icon={<UploadOutlined />} onClick={() => setImportOpen(true)}>
            Import Excel
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Thêm nhân viên
          </Button>
        </Space>
      </div>

      {/* Filters */}
      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Input
            placeholder="Tìm mã NV, họ tên..."
            prefix={<SearchOutlined />}
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            onPressEnter={fetchEmployees}
            allowClear
          />
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Select
            placeholder="Nhóm NV"
            value={filters.nhom_nv}
            onChange={(val) => handleFilterChange('nhom_nv', val)}
            allowClear
            style={{ width: '100%' }}
          >
            {NHOM_NV_OPTIONS.map((opt) => (
              <Option key={opt.value} value={opt.value}>{opt.label}</Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Select
            placeholder="Trạng thái"
            value={filters.trang_thai}
            onChange={(val) => handleFilterChange('trang_thai', val)}
            allowClear
            style={{ width: '100%' }}
          >
            {TRANG_THAI_OPTIONS.map((opt) => (
              <Option key={opt.value} value={opt.value}>{opt.label}</Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Select
            placeholder="Đơn vị"
            value={filters.don_vi_id}
            onChange={(val) => handleFilterChange('don_vi_id', val)}
            allowClear
            style={{ width: '100%' }}
            showSearch
            optionFilterProp="children"
          >
            {donViList.map((dv) => (
              <Option key={dv.id} value={dv.id}>{dv.ten}</Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={3}>
          <Button onClick={fetchEmployees} style={{ width: '100%' }}>
            Lọc
          </Button>
        </Col>
      </Row>

      {/* Table */}
      <Table
        dataSource={data}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        scroll={{ x: 1100 }}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Tổng ${total} nhân viên` }}
      />

      {/* Add/Edit Drawer */}
      <Drawer
        title={editingRecord ? 'Sửa nhân viên' : 'Thêm nhân viên'}
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); setEditingRecord(null); }}
        width={480}
        footer={
          <Space style={{ float: 'right' }}>
            <Button onClick={() => setDrawerOpen(false)}>Hủy</Button>
            <Button type="primary" onClick={() => form.submit()}>
              {editingRecord ? 'Cập nhật' : 'Thêm mới'}
            </Button>
          </Space>
        }
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="ma_nv"
            label="Mã nhân viên"
            rules={[{ required: true, message: 'Vui lòng nhập mã NV' }]}
          >
            <Input maxLength={20} disabled={!!editingRecord} />
          </Form.Item>

          <Form.Item
            name="ho_ten"
            label="Họ tên"
            rules={[{ required: true, message: 'Vui lòng nhập họ tên' }]}
          >
            <Input maxLength={100} />
          </Form.Item>

          <Form.Item
            name="nhom_nv"
            label="Nhóm nhân viên"
            rules={[{ required: true, message: 'Vui lòng chọn nhóm' }]}
          >
            <Select disabled={!!editingRecord}>
              {NHOM_NV_OPTIONS.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>

          {/* Conditional: ten_goi only shown when nhom_nv = GV */}
          {formNhomNv === 'GV' && (
            <Form.Item name="ten_goi" label="Tên gọi (biệt danh)">
              <Input maxLength={50} placeholder="Tên gọi trong trường" />
            </Form.Item>
          )}

          <Form.Item name="don_vi_id" label="Đơn vị">
            <Select allowClear placeholder="Chọn đơn vị" showSearch optionFilterProp="children">
              {donViList.map((dv) => (
                <Option key={dv.id} value={dv.id}>{dv.ten}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="chuc_vu_id" label="Chức vụ">
            <Select allowClear placeholder="Chọn chức vụ" showSearch optionFilterProp="children">
              {chucVuList.map((cv) => (
                <Option key={cv.id} value={cv.id}>{cv.ten}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="cap_bac_ql_id" label="Cấp bậc quản lý">
            <Select allowClear placeholder="Chọn cấp bậc" showSearch optionFilterProp="children">
              {capBacList.map((cb) => (
                <Option key={cb.id} value={cb.id}>{cb.ten}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="trang_thai"
            label="Trạng thái"
            rules={[{ required: true, message: 'Vui lòng chọn trạng thái' }]}
          >
            <Select>
              {TRANG_THAI_OPTIONS.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="email" label="Email">
            <Input type="email" maxLength={100} />
          </Form.Item>

          <Form.Item name="sdt" label="Số điện thoại">
            <Input maxLength={20} />
          </Form.Item>
        </Form>
      </Drawer>

      {/* Import Excel Modal */}
      <ImportExcel
        title="Import danh sách nhân viên"
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleImportConfirm}
        accept=".xlsx,.xls"
        maxSize={10}
      />
    </div>
  );
}
