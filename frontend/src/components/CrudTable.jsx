import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Space, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';

export default function CrudTable({ title, columns, fetchFn, createFn, updateFn, deleteFn, formFields }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form] = Form.useForm();

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchFn();
      setData(res.data);
    } catch (e) {
      message.error('Lỗi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleSubmit = async (values) => {
    try {
      if (editingRecord) {
        await updateFn(editingRecord.id, values);
        message.success('Cập nhật thành công');
      } else {
        await createFn(values);
        message.success('Thêm mới thành công');
      }
      setModalOpen(false);
      form.resetFields();
      setEditingRecord(null);
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteFn(id);
      message.success('Đã xóa');
      loadData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Không thể xóa');
    }
  };

  const actionCol = {
    title: 'Thao tác',
    key: 'actions',
    width: 120,
    render: (_, record) => (
      <Space>
        <Button
          size="small"
          icon={<EditOutlined />}
          onClick={() => {
            setEditingRecord(record);
            form.setFieldsValue(record);
            setModalOpen(true);
          }}
        />
        <Popconfirm title="Xác nhận xóa?" onConfirm={() => handleDelete(record.id)}>
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    ),
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>{title}</h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => { setEditingRecord(null); form.resetFields(); setModalOpen(true); }}
        >
          Thêm mới
        </Button>
      </div>
      <Table
        dataSource={data}
        columns={[...columns, actionCol]}
        rowKey="id"
        loading={loading}
        size="small"
      />
      <Modal
        title={editingRecord ? 'Sửa' : 'Thêm mới'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {formFields.map((f) => (
            <Form.Item key={f.name} name={f.name} label={f.label} rules={f.rules}>
              {f.component || <Input />}
            </Form.Item>
          ))}
        </Form>
      </Modal>
    </div>
  );
}
