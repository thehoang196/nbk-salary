import React from 'react';
import { InputNumber, DatePicker, Switch } from 'antd';
import CrudTable from '../../components/CrudTable';
import * as danhMucApi from '../../services/danhMucApi';

export default function HeSoLuong() {
  return (
    <CrudTable
      title="Quản lý Hệ số lương"
      columns={[
        { title: 'Bậc', dataIndex: 'bac' },
        { title: 'Hệ số', dataIndex: 'he_so' },
        { title: 'Ngày hiệu lực', dataIndex: 'ngay_hieu_luc' },
        {
          title: 'Trạng thái',
          dataIndex: 'is_active',
          render: (v) => (v ? 'Hoạt động' : 'Ngưng'),
        },
      ]}
      fetchFn={() => danhMucApi.getDanhMuc('he-so-luong')}
      createFn={(d) => danhMucApi.createDanhMuc('he-so-luong', d)}
      updateFn={(id, d) => danhMucApi.updateDanhMuc('he-so-luong', id, d)}
      deleteFn={(id) => danhMucApi.deleteDanhMuc('he-so-luong', id)}
      formFields={[
        { name: 'bac', label: 'Bậc', rules: [{ required: true, message: 'Vui lòng nhập bậc' }] },
        {
          name: 'he_so',
          label: 'Hệ số',
          rules: [{ required: true, message: 'Vui lòng nhập hệ số' }],
          component: <InputNumber style={{ width: '100%' }} min={0.01} max={99.99} step={0.01} />,
        },
        {
          name: 'ngay_hieu_luc',
          label: 'Ngày hiệu lực',
          rules: [{ required: true, message: 'Vui lòng chọn ngày hiệu lực' }],
          component: <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />,
        },
        {
          name: 'is_active',
          label: 'Hoạt động',
          component: <Switch />,
          valuePropName: 'checked',
          initialValue: true,
        },
      ]}
    />
  );
}
