import React from 'react';
import { InputNumber } from 'antd';
import CrudTable from '../../components/CrudTable';
import * as danhMucApi from '../../services/danhMucApi';

export default function CapBacQL() {
  const columns = [
    { title: 'Mã', dataIndex: 'ma', width: 120 },
    { title: 'Tên', dataIndex: 'ten' },
    {
      title: 'Đơn giá lương khoán',
      dataIndex: 'don_gia_luong_khoan',
      width: 200,
      render: (v) => v != null ? `${Number(v).toLocaleString('vi-VN')} VND` : '0 VND',
    },
  ];

  const formFields = [
    { name: 'ma', label: 'Mã', rules: [{ required: true, message: 'Vui lòng nhập mã' }] },
    { name: 'ten', label: 'Tên', rules: [{ required: true, message: 'Vui lòng nhập tên' }] },
    {
      name: 'don_gia_luong_khoan',
      label: 'Đơn giá lương khoán (VND)',
      rules: [
        { type: 'number', min: 0, max: 999999999, message: 'Giá trị từ 0 đến 999,999,999' },
      ],
      component: (
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          max={999999999}
          formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
          parser={(v) => v.replace(/,/g, '')}
          placeholder="Nhập đơn giá"
        />
      ),
    },
  ];

  return (
    <CrudTable
      title="Cấp bậc quản lý"
      columns={columns}
      fetchFn={danhMucApi.getCapBacQL}
      createFn={danhMucApi.createCapBacQL}
      updateFn={danhMucApi.updateCapBacQL}
      deleteFn={danhMucApi.deleteCapBacQL}
      formFields={formFields}
    />
  );
}
