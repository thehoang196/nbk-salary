import React from 'react';
import { Tabs, InputNumber } from 'antd';
import { useSearchParams } from 'react-router-dom';
import CrudTable from '../../components/CrudTable';
import * as danhMucApi from '../../services/danhMucApi';

const DonViTab = () => (
  <CrudTable
    title="Đơn vị"
    columns={[
      { title: 'Tên', dataIndex: 'ten' },
      { title: 'Mô tả', dataIndex: 'mo_ta' },
    ]}
    fetchFn={() => danhMucApi.getDanhMuc('don-vi')}
    createFn={(d) => danhMucApi.createDanhMuc('don-vi', d)}
    updateFn={(id, d) => danhMucApi.updateDanhMuc('don-vi', id, d)}
    deleteFn={(id) => danhMucApi.deleteDanhMuc('don-vi', id)}
    formFields={[
      { name: 'ten', label: 'Tên đơn vị', rules: [{ required: true }] },
      { name: 'mo_ta', label: 'Mô tả' },
    ]}
  />
);

const ChucVuTab = () => (
  <CrudTable
    title="Chức vụ"
    columns={[
      { title: 'Mã', dataIndex: 'ma' },
      { title: 'Tên', dataIndex: 'ten' },
      { title: 'Đơn giá lương khoán', dataIndex: 'don_gia_luong_khoan', render: (v) => `${(v || 0).toLocaleString()} đ` },
    ]}
    fetchFn={danhMucApi.getChucVu}
    createFn={danhMucApi.createChucVu}
    updateFn={danhMucApi.updateChucVu}
    deleteFn={danhMucApi.deleteChucVu}
    formFields={[
      { name: 'ma', label: 'Mã', rules: [{ required: true }] },
      { name: 'ten', label: 'Tên', rules: [{ required: true }] },
      {
        name: 'don_gia_luong_khoan',
        label: 'Đơn giá lương khoán (VND)',
        component: (
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
          />
        ),
      },
    ]}
  />
);

const CapBacQLTab = () => (
  <CrudTable
    title="Cấp bậc quản lý"
    columns={[
      { title: 'Mã', dataIndex: 'ma' },
      { title: 'Tên', dataIndex: 'ten' },
      { title: 'Đơn giá', dataIndex: 'don_gia_luong_khoan', render: (v) => `${(v || 0).toLocaleString()} đ` },
    ]}
    fetchFn={danhMucApi.getCapBacQL}
    createFn={danhMucApi.createCapBacQL}
    updateFn={danhMucApi.updateCapBacQL}
    deleteFn={danhMucApi.deleteCapBacQL}
    formFields={[
      { name: 'ma', label: 'Mã', rules: [{ required: true }] },
      { name: 'ten', label: 'Tên', rules: [{ required: true }] },
      {
        name: 'don_gia_luong_khoan',
        label: 'Đơn giá (VND)',
        component: <InputNumber style={{ width: '100%' }} min={0} />,
      },
    ]}
  />
);

const NghiepVuTab = () => (
  <CrudTable
    title="Nghiệp vụ"
    columns={[
      { title: 'Mã', dataIndex: 'ma' },
      { title: 'Tên', dataIndex: 'ten' },
    ]}
    fetchFn={danhMucApi.getNghiepVu}
    createFn={danhMucApi.createNghiepVu}
    updateFn={danhMucApi.updateNghiepVu}
    deleteFn={danhMucApi.deleteNghiepVu}
    formFields={[
      { name: 'ma', label: 'Mã', rules: [{ required: true }] },
      { name: 'ten', label: 'Tên', rules: [{ required: true }] },
    ]}
  />
);

const KiemNhiemTab = () => (
  <CrudTable
    title="Kiêm nhiệm"
    columns={[
      { title: 'Mã', dataIndex: 'ma' },
      { title: 'Tên', dataIndex: 'ten' },
    ]}
    fetchFn={danhMucApi.getKiemNhiem}
    createFn={danhMucApi.createKiemNhiem}
    updateFn={danhMucApi.updateKiemNhiem}
    deleteFn={danhMucApi.deleteKiemNhiem}
    formFields={[
      { name: 'ma', label: 'Mã', rules: [{ required: true }] },
      { name: 'ten', label: 'Tên', rules: [{ required: true }] },
    ]}
  />
);

const MonHocTab = () => (
  <CrudTable
    title="Môn học"
    columns={[
      { title: 'Mã môn', dataIndex: 'ma_mon' },
      { title: 'Tên', dataIndex: 'ten' },
    ]}
    fetchFn={() => danhMucApi.getDanhMuc('mon-hoc')}
    createFn={(d) => danhMucApi.createDanhMuc('mon-hoc', d)}
    updateFn={(id, d) => danhMucApi.updateDanhMuc('mon-hoc', id, d)}
    deleteFn={(id) => danhMucApi.deleteDanhMuc('mon-hoc', id)}
    formFields={[
      { name: 'ma_mon', label: 'Mã môn', rules: [{ required: true }] },
      { name: 'ten', label: 'Tên', rules: [{ required: true }] },
    ]}
  />
);

export default function DanhMuc() {
  const [searchParams, setSearchParams] = useSearchParams();

  const tabKeyMap = {
    'don-vi': '1',
    'chuc-vu': '2',
    'cap-bac-ql': '3',
    'nghiep-vu': '4',
    'kiem-nhiem': '5',
    'mon-hoc': '6',
    'he-so-luong': '7',
    'don-gia-day': '8',
  };

  const reverseTabMap = Object.fromEntries(Object.entries(tabKeyMap).map(([k, v]) => [v, k]));
  const tabParam = searchParams.get('tab');
  const activeKey = tabKeyMap[tabParam] || '1';

  const handleTabChange = (key) => {
    const slug = reverseTabMap[key];
    if (slug) {
      setSearchParams({ tab: slug });
    }
  };

  const items = [
    { key: '1', label: 'Đơn vị', children: <DonViTab /> },
    { key: '2', label: 'Chức vụ', children: <ChucVuTab /> },
    { key: '3', label: 'Cấp bậc QL', children: <CapBacQLTab /> },
    { key: '4', label: 'Nghiệp vụ', children: <NghiepVuTab /> },
    { key: '5', label: 'Kiêm nhiệm', children: <KiemNhiemTab /> },
    { key: '6', label: 'Môn học', children: <MonHocTab /> },
    { key: '7', label: 'Hệ số lương', children: <div>Hệ số lương - Coming Soon</div> },
    { key: '8', label: 'Đơn giá dạy', children: <div>Đơn giá dạy - Coming Soon</div> },
  ];

  return <Tabs items={items} activeKey={activeKey} onChange={handleTabChange} />;
}
