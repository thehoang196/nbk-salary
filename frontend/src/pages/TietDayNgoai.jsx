import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, Modal, Form, Select, InputNumber,
  DatePicker, message, Popconfirm, Typography, Tooltip,
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined,
  ReloadOutlined, UploadOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Title } = Typography;
const { Option } = Select;

const formatVND = (value) => {
  if (value == null) return '—';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(value);
};

export default function TietDayNgoai() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [saving, setSaving] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [form] = Form.useForm();

  // Dropdown data
  const [teachers, setTeachers] = useState([]);
  const [loaiList, setLoaiList] = useState([]);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Watch form fields for auto-calculating thanh_tien
  const soTiet = Form.useWatch('so_tiet', form);
  const donGia = Form.useWatch('don_gia', form);
  const heSo = Form.useWatch('he_so', form);

  const thanhTien = (soTiet || 0) * (donGia || 0) * (heSo || 1);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/tiet-ngoai/${thang}/${nam}`);
      setData(res.data);
    } catch (e) {
      message.error('Lỗi tải dữ liệu tiết dạy ngoài');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  const fetchDropdowns = useCallback(async () => {
    try {
      const [teacherRes, loaiRes] = await Promise.all([
        api.get('/nhan-vien', { params: { nhom_nv: 'GV' } }),
        api.get('/danh-muc/loai-tiet-ngoai'),
      ]);
      setTeachers(teacherRes.data);
      setLoaiList(loaiRes.data);
    } catch (e) {
      message.error('Lỗi tải danh mục');
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchDropdowns();
  }, [fetchDropdowns]);

  const handleMonthChange = (date) => {
    if (date) setSelectedMonth(date);
  };

  const openAddModal = () => {
    setEditingRecord(null);
    form.resetFields();
    form.setFieldsValue({ he_so: 1 });
    setModalOpen(true);
  };

  const openEditModal = (record) => {
    setEditingRecord(record);
    form.setFieldsValue({
      nhan_vien_id: record.nhan_vien_id,
      loai: record.loai,
      so_tiet: record.so_tiet,
      don_gia: record.don_gia,
      he_so: record.he_so,
    });
    setModalOpen(true);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setEditingRecord(null);
    form.resetFields();
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);

      const payload = {
        ...values,
        thang,
        nam,
      };

      if (editingRecord) {
        await api.put(`/tiet-ngoai/${editingRecord.id}`, payload);
        message.success('Cập nhật thành công');
      } else {
        await api.post('/tiet-ngoai', payload);
        message.success('Thêm mới thành công');
      }

      handleModalClose();
      fetchData();
    } catch (e) {
      if (e.errorFields) return; // Form validation error
      message.error(e.response?.data?.detail || 'Lỗi lưu dữ liệu');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/tiet-ngoai/${id}`);
      message.success('Đã xóa');
      fetchData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi xóa dữ liệu');
    }
  };

  const handleImport = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thang', thang);
    formData.append('nam', nam);

    const res = await api.post('/tiet-ngoai/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    fetchData();
    return res.data;
  };

  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Giáo viên',
      key: 'giao_vien',
      width: 180,
      render: (_, record) => record.ho_ten || record.ten_nhan_vien || '—',
    },
    {
      title: 'Loại',
      dataIndex: 'loai',
      key: 'loai',
      width: 150,
      render: (val) => {
        const found = loaiList.find((l) => l.ma === val || l.id === val);
        return found?.ten || val || '—';
      },
    },
    {
      title: 'Số tiết',
      dataIndex: 'so_tiet',
      key: 'so_tiet',
      width: 90,
      align: 'right',
      render: (val) => (val != null ? val : '—'),
    },
    {
      title: 'Đơn giá',
      dataIndex: 'don_gia',
      key: 'don_gia',
      width: 120,
      align: 'right',
      render: (val) => formatVND(val),
    },
    {
      title: 'Hệ số',
      dataIndex: 'he_so',
      key: 'he_so',
      width: 80,
      align: 'right',
      render: (val) => (val != null ? val : 1),
    },
    {
      title: 'Thành tiền',
      dataIndex: 'thanh_tien',
      key: 'thanh_tien',
      width: 140,
      align: 'right',
      render: (val, record) => {
        const computed = (record.so_tiet || 0) * (record.don_gia || 0) * (record.he_so || 1);
        return formatVND(val ?? computed);
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 100,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Sửa">
            <Button
              size="small"
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Xác nhận xóa?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
          >
            <Tooltip title="Xóa">
              <Button
                size="small"
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          Tiết dạy ngoài
        </Title>
        <Space>
          <DatePicker
            picker="month"
            value={selectedMonth}
            onChange={handleMonthChange}
            format="MM/YYYY"
            allowClear={false}
            style={{ width: 140 }}
          />
          <Tooltip title="Tải lại">
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading} />
          </Tooltip>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setImportOpen(true)}
          >
            Import Excel
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openAddModal}
          >
            Thêm mới
          </Button>
        </Space>
      </div>

      <Table
        dataSource={data}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        bordered
        scroll={{ x: 1000 }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100'],
          showTotal: (total) => `Tổng ${total} dòng`,
        }}
      />

      {/* Add/Edit Modal */}
      <Modal
        title={editingRecord ? 'Sửa tiết dạy ngoài' : 'Thêm tiết dạy ngoài'}
        open={modalOpen}
        onCancel={handleModalClose}
        onOk={handleSave}
        confirmLoading={saving}
        okText="Lưu"
        cancelText="Hủy"
        width={520}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ he_so: 1 }}
        >
          <Form.Item
            name="nhan_vien_id"
            label="Giáo viên"
            rules={[{ required: true, message: 'Vui lòng chọn giáo viên' }]}
          >
            <Select
              showSearch
              placeholder="Chọn giáo viên"
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
            >
              {teachers.map((t) => (
                <Option key={t.id} value={t.id}>
                  {t.ho_ten}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="loai"
            label="Loại tiết ngoài"
            rules={[{ required: true, message: 'Vui lòng chọn loại' }]}
          >
            <Select placeholder="Chọn loại tiết ngoài">
              {loaiList.map((l) => (
                <Option key={l.ma || l.id} value={l.ma || l.id}>
                  {l.ten}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="so_tiet"
            label="Số tiết"
            rules={[{ required: true, message: 'Vui lòng nhập số tiết' }]}
          >
            <InputNumber
              min={0}
              max={999}
              step={0.5}
              precision={1}
              style={{ width: '100%' }}
              placeholder="Nhập số tiết"
            />
          </Form.Item>

          <Form.Item
            name="don_gia"
            label="Đơn giá (VNĐ)"
            rules={[{ required: true, message: 'Vui lòng nhập đơn giá' }]}
          >
            <InputNumber
              min={0}
              step={10000}
              style={{ width: '100%' }}
              placeholder="Nhập đơn giá"
              formatter={(value) =>
                value ? `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : ''
              }
              parser={(value) => value.replace(/,/g, '')}
            />
          </Form.Item>

          <Form.Item
            name="he_so"
            label="Hệ số"
            rules={[{ required: true, message: 'Vui lòng nhập hệ số' }]}
          >
            <InputNumber
              min={0.1}
              max={10}
              step={0.1}
              precision={2}
              style={{ width: '100%' }}
              placeholder="Nhập hệ số"
            />
          </Form.Item>

          <div
            style={{
              background: '#f6ffed',
              border: '1px solid #b7eb8f',
              borderRadius: 6,
              padding: '12px 16px',
              textAlign: 'center',
            }}
          >
            <span style={{ color: '#666', marginRight: 8 }}>Thành tiền:</span>
            <strong style={{ fontSize: 16, color: '#389e0d' }}>
              {formatVND(thanhTien)}
            </strong>
          </div>
        </Form>
      </Modal>

      {/* Import Excel Modal */}
      <ImportExcel
        title="Import tiết dạy ngoài"
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleImport}
      />
    </div>
  );
}
