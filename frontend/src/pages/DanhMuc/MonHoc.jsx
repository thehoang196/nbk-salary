import React from 'react';
import { Switch } from 'antd';
import CrudTable from '../../components/CrudTable';
import * as danhMucApi from '../../services/danhMucApi';

export default function MonHoc() {
  return (
    <CrudTable
      title="Quản lý Môn học"
      columns={[
        { title: 'Mã môn', dataIndex: 'ma_mon' },
        { title: 'Tên', dataIndex: 'ten' },
        {
          title: 'Trạng thái',
          dataIndex: 'is_active',
          render: (v) => (v ? 'Hoạt động' : 'Ngưng'),
        },
      ]}
      fetchFn={() => danhMucApi.getDanhMuc('mon-hoc')}
      createFn={(d) => danhMucApi.createDanhMuc('mon-hoc', d)}
      updateFn={(id, d) => danhMucApi.updateDanhMuc('mon-hoc', id, d)}
      deleteFn={(id) => danhMucApi.deleteDanhMuc('mon-hoc', id)}
      formFields={[
        { name: 'ma_mon', label: 'Mã môn', rules: [{ required: true, message: 'Vui lòng nhập mã môn' }] },
        { name: 'ten', label: 'Tên môn học', rules: [{ required: true, message: 'Vui lòng nhập tên môn học' }] },
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
