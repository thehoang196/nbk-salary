import React, { useState } from 'react';
import { Tabs, InputNumber, Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import CrudTable from '../../components/CrudTable';
import ImportExcel from '../../components/ImportExcel';
import * as danhMucApi from '../../services/danhMucApi';
import api from '../../services/api';

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

const HeSoLuongTab = () => (
  <CrudTable
    title="Hệ số lương"
    columns={[
      { title: 'Bậc', dataIndex: 'bac' },
      { title: 'Hệ số', dataIndex: 'he_so' },
      {
        title: 'Trạng thái',
        dataIndex: 'is_active',
        render: (v) => (v ? 'Hoạt động' : 'Ngưng'),
      },
    ]}
    fetchFn={() => danhMucApi.getDanhMuc('he-so-luong')}
    createFn={(d) => danhMucApi.createDanhMuc('he-so-luong', d)}
    deleteFn={(id) => danhMucApi.deleteDanhMuc('he-so-luong', id)}
    formFields={[
      { name: 'bac', label: 'Bậc', rules: [{ required: true, message: 'Vui lòng nhập bậc' }] },
      {
        name: 'he_so',
        label: 'Hệ số',
        rules: [{ required: true, message: 'Vui lòng nhập hệ số' }],
        component: <InputNumber style={{ width: '100%' }} min={0.01} max={99.99} step={0.01} />,
      },
    ]}
  />
);

const DonGiaDayTab = () => (
  <CrudTable
    title="Đơn giá dạy"
    columns={[
      { title: 'Giáo viên (ID)', dataIndex: 'nhan_vien_id' },
      { title: 'Môn học (ID)', dataIndex: 'mon_hoc_id' },
      { title: 'Khối (ID)', dataIndex: 'khoi_id' },
      { title: 'Đơn giá', dataIndex: 'don_gia', render: (v) => v != null ? `${Number(v).toLocaleString()} đ` : '—' },
      { title: 'Ngày bắt đầu', dataIndex: 'ngay_bat_dau' },
      {
        title: 'Trạng thái',
        dataIndex: 'is_active',
        render: (v) => (v ? 'Hoạt động' : 'Ngưng'),
      },
    ]}
    fetchFn={() => danhMucApi.getDonGiaDay()}
    createFn={(d) => danhMucApi.createDonGiaDay(d)}
    updateFn={(id, d) => danhMucApi.updateDonGiaDay(id, d)}
    deleteFn={(id) => danhMucApi.deleteDonGiaDay(id)}
    formFields={[
      { name: 'nhan_vien_id', label: 'Giáo viên (ID)', rules: [{ required: true, message: 'Bắt buộc' }], component: <InputNumber style={{ width: '100%' }} min={1} /> },
      { name: 'mon_hoc_id', label: 'Môn học (ID)', rules: [{ required: true, message: 'Bắt buộc' }], component: <InputNumber style={{ width: '100%' }} min={1} /> },
      { name: 'khoi_id', label: 'Khối (ID)', rules: [{ required: true, message: 'Bắt buộc' }], component: <InputNumber style={{ width: '100%' }} min={1} /> },
      { name: 'don_gia', label: 'Đơn giá (VND)', rules: [{ required: true, message: 'Bắt buộc' }], component: <InputNumber style={{ width: '100%' }} min={1} /> },
    ]}
  />
);

export default function DanhMuc() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [importGVOpen, setImportGVOpen] = useState(false);

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
    { key: '7', label: 'Hệ số lương', children: <HeSoLuongTab /> },
    { key: '8', label: 'Đơn giá dạy', children: <DonGiaDayTab /> },
  ];

  const handleImportGVConfirm = async (file) => {
    const XLSX = await import('xlsx');
    const arrayBuffer = await file.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const jsonData = XLSX.utils.sheet_to_json(sheet, { defval: '' });

    // Map Excel columns to API fields - specifically for GV (teachers)
    const rows = jsonData.map((row) => ({
      ma_nv: String(row['Mã NV'] || row['ma_nv'] || '').trim(),
      ho_ten: String(row['Họ tên'] || row['ho_ten'] || '').trim(),
      nhom_nv: 'GV',
      don_vi: String(row['Đơn vị'] || row['don_vi'] || '').trim() || null,
      chuc_vu: String(row['Chức vụ'] || row['chuc_vu'] || '').trim() || null,
      cap_bac_ql: String(row['Cấp bậc QL'] || row['cap_bac_ql'] || '').trim() || null,
      ten_goi: String(row['Tên gọi'] || row['ten_goi'] || '').trim() || null,
      email: String(row['Email'] || row['email'] || '').trim() || null,
      sdt: String(row['SĐT'] || row['sdt'] || '').trim() || null,
    }));

    const res = await api.post('/nhan-vien/import', { rows });
    return res.data;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý Giáo viên</h2>
        <Button icon={<UploadOutlined />} onClick={() => setImportGVOpen(true)}>
          Import giáo viên từ Excel
        </Button>
      </div>
      <Tabs items={items} activeKey={activeKey} onChange={handleTabChange} destroyInactiveTabPane />
      <ImportExcel
        title="Import danh sách giáo viên"
        open={importGVOpen}
        onClose={() => setImportGVOpen(false)}
        onConfirm={handleImportGVConfirm}
        accept=".xlsx,.xls"
        maxSize={10}
      />
    </div>
  );
}
