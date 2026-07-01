import React, { useState } from 'react';
import { Card, Tabs, Button, Upload, message, Alert, Table, Space, Typography } from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const IMPORT_FORMS = [
  {
    key: 'ho-so',
    label: 'Hồ sơ nhân viên',
    description: 'Import thông tin nhân viên từ MISA (Mã NV, Họ tên, CCCD, Đơn vị, Vị trí...)',
    endpoint: '/nhan-vien/import',
  },
  {
    key: 'gia-dinh',
    label: 'Thông tin gia đình',
    description: 'Import người thân / người phụ thuộc cho nhân viên',
    endpoint: '/misa-hr/import/gia-dinh',
  },
  {
    key: 'lich-su-luong',
    label: 'Lịch sử lương',
    description: 'Import lịch sử lương (lương cơ bản, phụ cấp, khấu trừ)',
    endpoint: '/misa-hr/import/lich-su-luong',
  },
  {
    key: 'qua-trinh-ct',
    label: 'Quá trình công tác',
    description: 'Import quá trình công tác, thuyên chuyển',
    endpoint: '/misa-hr/import/qua-trinh-ct',
  },
  {
    key: 'bang-cap',
    label: 'Bằng cấp',
    description: 'Import trình độ đào tạo, bằng cấp, chứng chỉ',
    endpoint: '/misa-hr/import/bang-cap',
  },
  {
    key: 'nghi-phep',
    label: 'Tổng hợp nghỉ phép',
    description: 'Import số ngày phép năm (phép năm nay, năm trước, thâm niên...)',
    endpoint: '/misa-hr/import/nghi-phep',
  },
  {
    key: 'co-cau-to-chuc',
    label: 'Cơ cấu tổ chức',
    description: 'Import đơn vị, phòng ban từ MISA (Mã đơn vị, Tên, Cấp tổ chức...)',
    endpoint: '/misa-hr/import/co-cau-to-chuc',
  },
  {
    key: 'vi-tri-cong-viec',
    label: 'Vị trí công việc',
    description: 'Import vị trí công việc (Mã vị trí, Tên, Đơn vị, Nhóm vị trí...)',
    endpoint: '/misa-hr/import/vi-tri-cong-viec',
  },
  {
    key: 'cham-cong',
    label: 'Chấm công (MISA)',
    description: 'Import tổng hợp chấm công VP từ file MISA',
    endpoint: '/cham-cong/import-misa',
  },
];

export default function MisaImport() {
  const [activeTab, setActiveTab] = useState('ho-so');
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [currentForm, setCurrentForm] = useState(null);

  const handleOpenImport = (form) => {
    setCurrentForm(form);
    setImportModalOpen(true);
  };

  const handleImportConfirm = async (file) => {
    if (!currentForm) return {};
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post(
      `${currentForm.endpoint}/upload`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return res.data;
  };

  const tabItems = IMPORT_FORMS.map((form) => ({
    key: form.key,
    label: form.label,
    children: (
      <Card size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text type="secondary">{form.description}</Text>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => handleOpenImport(form)}
          >
            Import từ Excel
          </Button>
        </Space>
      </Card>
    ),
  }));

  return (
    <div>
      <Title level={3}>Import dữ liệu MISA</Title>
      <Alert
        type="info"
        showIcon
        message="Hỗ trợ import dữ liệu từ các form mẫu MISA AMIS"
        description="Chọn loại dữ liệu cần import, tải file Excel theo mẫu MISA và upload."
        style={{ marginBottom: 16 }}
      />
      <Tabs
        items={tabItems}
        activeKey={activeTab}
        onChange={setActiveTab}
        tabPosition="left"
      />
      <ImportExcel
        title={currentForm ? `Import ${currentForm.label}` : 'Import'}
        open={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onConfirm={handleImportConfirm}
      />
    </div>
  );
}
