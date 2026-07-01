import React from 'react';
import { InputNumber } from 'antd';
import CrudTable from '../../components/CrudTable';
import { getChucVu, createChucVu, updateChucVu, deleteChucVu } from '../../services/danhMucApi';

const columns = [
  { title: 'Mã', dataIndex: 'ma', width: 120 },
  { title: 'Tên chức vụ', dataIndex: 'ten' },
  {
    title: 'Đơn giá lương khoán (VND)',
    dataIndex: 'don_gia_luong_khoan',
    width: 220,
    render: (v) => (v != null ? `${Number(v).toLocaleString('vi-VN')} đ` : '0 đ'),
  },
];

const formFields = [
  {
    name: 'ma',
    label: 'Mã chức vụ',
    rules: [{ required: true, message: 'Vui lòng nhập mã chức vụ' }],
  },
  {
    name: 'ten',
    label: 'Tên chức vụ',
    rules: [{ required: true, message: 'Vui lòng nhập tên chức vụ' }],
  },
  {
    name: 'don_gia_luong_khoan',
    label: 'Đơn giá lương khoán (VND)',
    rules: [
      {
        type: 'number',
        min: 0,
        max: 999999999,
        message: 'Đơn giá phải từ 0 đến 999,999,999 VND',
      },
    ],
    component: (
      <InputNumber
        style={{ width: '100%' }}
        min={0}
        max={999999999}
        step={100000}
        formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
        parser={(v) => v.replace(/,/g, '')}
        placeholder="0"
      />
    ),
  },
];

export default function ChucVu() {
  return (
    <CrudTable
      title="Quản lý Chức vụ"
      columns={columns}
      fetchFn={getChucVu}
      createFn={createChucVu}
      updateFn={updateChucVu}
      deleteFn={deleteChucVu}
      formFields={formFields}
    />
  );
}
