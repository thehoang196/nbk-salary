import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, DatePicker, message, Modal, Form, Select,
  InputNumber, Input, Card, Typography, Popconfirm, Tag,
} from 'antd';
import {
  PlusOutlined, UploadOutlined, DeleteOutlined, EditOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Title } = Typography;

export default function HoTroLuong() {
  // State
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [employees, setEmployees] = useState([]);
  const [loaiHoTroList, setLoaiHoTroList] = useState([]);

  // Single entry modal
  const [singleModalOpen, setSingleModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [singleForm] = Form.useForm();
  const [singleLoading, setSingleLoading] = useState(false);

  // Batch entry modal
  const [batchModalOpen, setBatchModalOpen] = useState(false);
  const [batchForm] = Form.useForm();
  const [batchLoading, setBatchLoading] = useState(false);

  // Import modal
  const [importOpen, setImportOpen] = useState(false);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch support allowance data
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/ho-tro-luong/${thang}/${nam}`);
      setData(res.data);
    } catch (e) {
      if (e.response?.status !== 404) {
        message.error('Lỗi tải dữ liệu hỗ trợ lương');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  // Fetch employees list
  const fetchEmployees = useCallback(async () => {
    try {
      const res = await api.get('/nhan-vien');
      const list = res.data?.items || res.data || [];
      setEmployees(list);
    } catch {
      setEmployees([]);
    }
  }, []);

  // Fetch allowance types
  const fetchLoaiHoTro = useCallback(async () => {
    try {
      const res = await api.get('/danh-muc/loai-ho-tro');
      const list = res.data?.data || res.data || [];
      setLoaiHoTroList(list);
    } catch {
      setLoaiHoTroList([]);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchEmployees();
    fetchLoaiHoTro();
  }, [fetchEmployees, fetchLoaiHoTro]);

  // Month change handler
  const handleMonthChange = (date) => {
    if (date) setSelectedMonth(date);
  };

  // ==========================================================================
  // Single entry CRUD
  // ==========================================================================

  const openSingleModal = (record = null) => {
    setEditingRecord(record);
    if (record) {
      singleForm.setFieldsValue({
        nhan_vien_id: record.nhan_vien_id,
        loai_ho_tro: record.loai_ho_tro,
        so_tien: record.so_tien,
        ghi_chu: record.ghi_chu,
      });
    } else {
      singleForm.resetFields();
    }
    setSingleModalOpen(true);
  };

  const handleSingleSubmit = async () => {
    try {
      const values = await singleForm.validateFields();
      setSingleLoading(true);

      if (editingRecord) {
        // Update existing
        await api.put(`/ho-tro-luong/${editingRecord.id}`, {
          loai_ho_tro: values.loai_ho_tro,
          so_tien: values.so_tien,
          ghi_chu: values.ghi_chu,
        });
        message.success('Cập nhật thành công');
      } else {
        // Create new
        await api.post('/ho-tro-luong', {
          nhan_vien_id: values.nhan_vien_id,
          thang,
          nam,
          loai_ho_tro: values.loai_ho_tro,
          so_tien: values.so_tien,
          ghi_chu: values.ghi_chu,
        });
        message.success('Thêm mới thành công');
      }

      setSingleModalOpen(false);
      singleForm.resetFields();
      setEditingRecord(null);
      fetchData();
    } catch (e) {
      if (e.response?.data?.detail) {
        message.error(e.response.data.detail);
      }
    } finally {
      setSingleLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/ho-tro-luong/${id}`);
      message.success('Đã xóa');
      fetchData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi khi xóa');
    }
  };

  // ==========================================================================
  // Batch entry
  // ==========================================================================

  const openBatchModal = () => {
    batchForm.resetFields();
    setBatchModalOpen(true);
  };

  const handleBatchSubmit = async () => {
    try {
      const values = await batchForm.validateFields();
      setBatchLoading(true);

      const entries = values.entries.map((entry) => ({
        nhan_vien_id: entry.nhan_vien_id,
        so_tien: entry.so_tien,
        ghi_chu: entry.ghi_chu || null,
      }));

      await api.post('/ho-tro-luong/batch', {
        thang,
        nam,
        loai_ho_tro: values.loai_ho_tro,
        entries,
      });

      message.success(`Đã thêm ${entries.length} khoản hỗ trợ`);
      setBatchModalOpen(false);
      batchForm.resetFields();
      fetchData();
    } catch (e) {
      if (e.response?.data?.detail) {
        message.error(e.response.data.detail);
      }
    } finally {
      setBatchLoading(false);
    }
  };

  // ==========================================================================
  // Import Excel
  // ==========================================================================

  const handleImportConfirm = async (file) => {
    // Read file and parse with xlsx (use FormData approach for backend)
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thang', thang);
    formData.append('nam', nam);

    const res = await api.post('/ho-tro-luong/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const result = res.data;
    if (result.errors?.length > 0) {
      fetchData();
      return {
        imported_count: result.imported_count,
        errors: result.errors.map((e) => ({
          row: e.row,
          message: e.error || e.message,
        })),
      };
    }

    fetchData();
    return { imported_count: result.imported_count };
  };

  // ==========================================================================
  // Table config
  // ==========================================================================

  // Build employee lookup map
  const employeeMap = {};
  employees.forEach((nv) => {
    employeeMap[nv.id] = nv.ho_ten || nv.ten_goi || nv.ma_nv;
  });

  const columns = [
    {
      title: 'Nhân viên',
      dataIndex: 'nhan_vien_id',
      key: 'nhan_vien',
      render: (id) => employeeMap[id] || `NV #${id}`,
      sorter: (a, b) => (employeeMap[a.nhan_vien_id] || '').localeCompare(employeeMap[b.nhan_vien_id] || ''),
    },
    {
      title: 'Loại hỗ trợ',
      dataIndex: 'loai_ho_tro',
      key: 'loai_ho_tro',
      render: (val) => <Tag color="blue">{val}</Tag>,
      filters: loaiHoTroList.map((l) => ({ text: l.ten, value: l.ten })),
      onFilter: (value, record) => record.loai_ho_tro === value,
    },
    {
      title: 'Số tiền (VND)',
      dataIndex: 'so_tien',
      key: 'so_tien',
      align: 'right',
      render: (val) => (val || 0).toLocaleString('vi-VN'),
      sorter: (a, b) => a.so_tien - b.so_tien,
    },
    {
      title: 'Ghi chú',
      dataIndex: 'ghi_chu',
      key: 'ghi_chu',
      ellipsis: true,
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => openSingleModal(record)}
          />
          <Popconfirm
            title="Xác nhận xóa?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div>
      <Title level={4}>Các khoản hỗ trợ khác theo lương</Title>

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
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openSingleModal(null)}
          >
            Thêm mới
          </Button>
          <Button
            icon={<TeamOutlined />}
            onClick={openBatchModal}
          >
            Nhập hàng loạt
          </Button>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setImportOpen(true)}
          >
            Import Excel
          </Button>
        </Space>
      </Card>

      {/* Data table */}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 50, showSizeChanger: true, showTotal: (t) => `Tổng: ${t} dòng` }}
        size="small"
        bordered
      />

      {/* Single entry Modal */}
      <Modal
        title={editingRecord ? 'Sửa khoản hỗ trợ' : 'Thêm khoản hỗ trợ'}
        open={singleModalOpen}
        onCancel={() => { setSingleModalOpen(false); setEditingRecord(null); }}
        onOk={handleSingleSubmit}
        confirmLoading={singleLoading}
        okText={editingRecord ? 'Cập nhật' : 'Thêm'}
        cancelText="Hủy"
        destroyOnClose
      >
        <Form form={singleForm} layout="vertical">
          <Form.Item
            name="nhan_vien_id"
            label="Nhân viên"
            rules={[{ required: true, message: 'Chọn nhân viên' }]}
          >
            <Select
              showSearch
              placeholder="Chọn nhân viên"
              optionFilterProp="label"
              disabled={!!editingRecord}
              options={employees.map((nv) => ({
                value: nv.id,
                label: `${nv.ho_ten}${nv.ma_nv ? ` (${nv.ma_nv})` : ''}`,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="loai_ho_tro"
            label="Loại hỗ trợ"
            rules={[{ required: true, message: 'Chọn loại hỗ trợ' }]}
          >
            <Select
              showSearch
              placeholder="Chọn loại hỗ trợ"
              optionFilterProp="label"
              options={loaiHoTroList.map((l) => ({
                value: l.ten,
                label: l.ten,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="so_tien"
            label="Số tiền (VND)"
            rules={[{ required: true, message: 'Nhập số tiền' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              max={999999999}
              formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(v) => v.replace(/,/g, '')}
              placeholder="Nhập số tiền"
            />
          </Form.Item>
          <Form.Item name="ghi_chu" label="Ghi chú">
            <Input.TextArea rows={2} maxLength={255} placeholder="Ghi chú (tùy chọn)" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Batch entry Modal */}
      <Modal
        title="Nhập hàng loạt hỗ trợ lương"
        open={batchModalOpen}
        onCancel={() => setBatchModalOpen(false)}
        onOk={handleBatchSubmit}
        confirmLoading={batchLoading}
        okText="Xác nhận"
        cancelText="Hủy"
        width={700}
        destroyOnClose
      >
        <Form form={batchForm} layout="vertical">
          <Form.Item
            name="loai_ho_tro"
            label="Loại hỗ trợ"
            rules={[{ required: true, message: 'Chọn loại hỗ trợ' }]}
          >
            <Select
              showSearch
              placeholder="Chọn loại hỗ trợ áp dụng"
              optionFilterProp="label"
              options={loaiHoTroList.map((l) => ({
                value: l.ten,
                label: l.ten,
              }))}
            />
          </Form.Item>

          <Form.List
            name="entries"
            rules={[
              {
                validator: async (_, entries) => {
                  if (!entries || entries.length === 0) {
                    return Promise.reject(new Error('Thêm ít nhất 1 nhân viên'));
                  }
                },
              },
            ]}
          >
            {(fields, { add, remove }, { errors }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'nhan_vien_id']}
                      rules={[{ required: true, message: 'Chọn NV' }]}
                      style={{ width: 220 }}
                    >
                      <Select
                        showSearch
                        placeholder="Chọn nhân viên"
                        optionFilterProp="label"
                        options={employees.map((nv) => ({
                          value: nv.id,
                          label: `${nv.ho_ten}${nv.ma_nv ? ` (${nv.ma_nv})` : ''}`,
                        }))}
                      />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'so_tien']}
                      rules={[{ required: true, message: 'Nhập số tiền' }]}
                      style={{ width: 180 }}
                    >
                      <InputNumber
                        style={{ width: '100%' }}
                        min={0}
                        max={999999999}
                        formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={(v) => v.replace(/,/g, '')}
                        placeholder="Số tiền"
                      />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'ghi_chu']}
                      style={{ width: 150 }}
                    >
                      <Input placeholder="Ghi chú" maxLength={255} />
                    </Form.Item>
                    <Button
                      type="link"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => remove(name)}
                    />
                  </Space>
                ))}
                <Form.Item>
                  <Button
                    type="dashed"
                    onClick={() => add()}
                    block
                    icon={<PlusOutlined />}
                  >
                    Thêm nhân viên
                  </Button>
                  <Form.ErrorList errors={errors} />
                </Form.Item>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>

      {/* Import Excel Modal */}
      <ImportExcel
        title={`Import hỗ trợ lương tháng ${thang}/${nam}`}
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleImportConfirm}
      />
    </div>
  );
}
