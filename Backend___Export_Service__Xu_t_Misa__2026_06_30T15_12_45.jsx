
// ============================================================
// FILE: frontend/src/pages/ThoiKhoaBieu/TKBManager.jsx
// Quản lý Thời khóa biểu + Thay đổi người dạy
// ============================================================

import React, { useState, useEffect } from 'react';
import { Table, Button, Upload, Modal, Form, Select, DatePicker, Tag, message, Card, Tabs } from 'antd';
import { UploadOutlined, SwapOutlined, CalendarOutlined } from '@ant-design/icons';
import { tkbApi } from '../../services/api';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;

const TKBManager = () => {
  const [tkbData, setTkbData] = useState([]);
  const [thayDoiData, setThayDoiData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadTKB();
    loadThayDoi();
  }, []);

  const loadTKB = async () => {
    setLoading(true);
    const data = await tkbApi.getAll();
    setTkbData(data);
    setLoading(false);
  };

  const loadThayDoi = async () => {
    const data = await tkbApi.getThayDoi();
    setThayDoiData(data);
  };

  // Import TKB từ Excel
  const handleImport = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const result = await tkbApi.importExcel(formData);
      message.success(`Import thành công: ${result.count} bản ghi`);
      loadTKB();
    } catch (error) {
      message.error('Import thất bại: ' + error.message);
    }
    return false;
  };

  // Tạo thay đổi người dạy
  const handleThayDoi = async (values) => {
    try {
      await tkbApi.createThayDoi(values);
      message.success('Đã tạo thay đổi người dạy');
      setModalVisible(false);
      form.resetFields();
      loadThayDoi();
    } catch (error) {
      message.error('Lỗi: ' + error.message);
    }
  };

  // Columns cho bảng TKB
  const tkbColumns = [
    { title: 'Giáo viên', dataIndex: 'ten_gv', key: 'ten_gv', fixed: 'left', width: 120 },
    { title: 'Môn học', dataIndex: 'ten_mon', key: 'ten_mon', width: 150 },
    { title: 'Khối', dataIndex: 'ten_khoi', key: 'ten_khoi', width: 80 },
    { title: 'Lớp', dataIndex: 'ten_lop', key: 'ten_lop', width: 80 },
    { title: 'Số tiết/tuần', dataIndex: 'so_tiet_tuan', key: 'so_tiet_tuan', width: 100 },
    { title: 'Đơn giá/tiết', dataIndex: 'don_gia_tiet', key: 'don_gia_tiet', width: 120,
      render: (val) => val ? `${val.toLocaleString()}đ` : '-' },
    {
      title: 'Trạng thái', key: 'status', width: 100,
      render: (_, record) => record.has_thay_doi ? 
        <Tag color="orange">Đã thay đổi</Tag> : 
        <Tag color="green">Bình thường</Tag>
    },
    {
      title: 'Thao tác', key: 'action', width: 100,
      render: (_, record) => (
        <Button 
          icon={<SwapOutlined />} 
          size="small"
          onClick={() => { form.setFieldsValue({ tkb_id: record.id }); setModalVisible(true); }}
        >
          Thay GV
        </Button>
      )
    }
  ];

  // Columns cho bảng Thay đổi
  const thayDoiColumns = [
    { title: 'GV gốc', dataIndex: 'ten_gv_goc', key: 'gv_goc' },
    { title: 'GV thay thế', dataIndex: 'ten_gv_thay_the', key: 'gv_thay' },
    { title: 'Môn', dataIndex: 'ten_mon', key: 'mon' },
    { title: 'Lớp', dataIndex: 'ten_lop', key: 'lop' },
    { title: 'Từ ngày', dataIndex: 'ngay_bat_dau', key: 'tu_ngay' },
    { title: 'Đến ngày', dataIndex: 'ngay_ket_thuc', key: 'den_ngay', 
      render: (val) => val || 'Vĩnh viễn' },
    { title: 'Lý do', dataIndex: 'ly_do', key: 'ly_do' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="Quản lý Thời khóa biểu" 
        extra={
          <Upload beforeUpload={handleImport} showUploadList={false} accept=".xlsx,.xls">
            <Button icon={<UploadOutlined />} type="primary">Import TKB (Excel)</Button>
          </Upload>
        }
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab={<span><CalendarOutlined />TKB Gốc</span>} key="1">
            <Table 
              columns={tkbColumns} 
              dataSource={tkbData} 
              loading={loading}
              rowKey="id"
              scroll={{ x: 1000 }}
              pagination={{ pageSize: 20 }}
            />
          </TabPane>
          <TabPane tab={<span><SwapOutlined />Thay đổi người dạy</span>} key="2">
            <Table 
              columns={thayDoiColumns} 
              dataSource={thayDoiData}
              rowKey="id"
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Modal thay đổi người dạy */}
      <Modal
        title="Thay đổi người dạy"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleThayDoi} layout="vertical">
          <Form.Item name="tkb_id" hidden><input /></Form.Item>
          <Form.Item name="gv_thay_the_id" label="GV thay thế" rules={[{ required: true }]}>
            <Select placeholder="Chọn giáo viên thay thế" showSearch optionFilterProp="children">
              {/* Options loaded from API */}
            </Select>
          </Form.Item>
          <Form.Item name="date_range" label="Thời gian" rules={[{ required: true }]}>
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="ly_do" label="Lý do">
            <Select placeholder="Chọn lý do">
              <Select.Option value="Nghỉ thai sản">Nghỉ thai sản</Select.Option>
              <Select.Option value="Nghỉ ốm">Nghỉ ốm</Select.Option>
              <Select.Option value="Đi công tác">Đi công tác</Select.Option>
              <Select.Option value="Nghỉ phép">Nghỉ phép</Select.Option>
              <Select.Option value="Khác">Khác</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TKBManager;


// ============================================================
// FILE: frontend/src/pages/Luong/BangLuong.jsx
// Bảng lương tháng + Phê duyệt
// ============================================================

import React, { useState, useEffect } from 'react';
import { Table, Button, Select, Card, Tag, Space, Modal, Statistic, Row, Col, message } from 'antd';
import { CalculatorOutlined, CheckCircleOutlined, FileExcelOutlined, FilePdfOutlined } from '@ant-design/icons';
import { luongApi } from '../../services/api';

const BangLuong = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [thang, setThang] = useState(new Date().getMonth() + 1);
  const [nam, setNam] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState({});

  useEffect(() => {
    loadBangLuong();
  }, [thang, nam]);

  const loadBangLuong = async () => {
    setLoading(true);
    const result = await luongApi.getBangLuong(thang, nam);
    setData(result);
    calculateSummary(result);
    setLoading(false);
  };

  const calculateSummary = (data) => {
    setSummary({
      tongNV: data.length,
      tongThuNhap: data.reduce((sum, r) => sum + r.tong_thu_nhap, 0),
      tongThucLinh: data.reduce((sum, r) => sum + r.thuc_linh, 0),
      tongBH: data.reduce((sum, r) => sum + r.bhxh + r.bhyt + r.bhtn, 0),
    });
  };

  const handleTinhLuong = async () => {
    Modal.confirm({
      title: `Tính lương tháng ${thang}/${nam}?`,
      content: 'Hệ thống sẽ tính lương cho tất cả nhân viên. Bảng lương cũ (nếu có) sẽ bị ghi đè.',
      onOk: async () => {
        setLoading(true);
        try {
          const result = await luongApi.tinhLuong(thang, nam);
          message.success(result.message);
          if (result.errors.length > 0) {
            message.warning(`Có ${result.errors.length} lỗi. Kiểm tra chi tiết.`);
          }
          loadBangLuong();
        } catch (error) {
          message.error('Lỗi tính lương: ' + error.message);
        }
        setLoading(false);
      }
    });
  };

  const handleExportMisa = async () => {
    const blob = await luongApi.exportMisa(thang, nam);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Luong_Misa_T${thang}_${nam}.xlsx`;
    a.click();
  };

  const columns = [
    { title: 'STT', key: 'stt', width: 50, render: (_, __, idx) => idx + 1 },
    { title: 'Mã NV', dataIndex: 'ma_nv', width: 80, fixed: 'left' },
    { title: 'Họ tên', dataIndex: 'ho_ten', width: 150, fixed: 'left' },
    { title: 'Chức danh', dataIndex: 'chuc_danh', width: 100 },
    { title: 'Lương CD', dataIndex: 'luong_chuc_danh', width: 110, 
      render: (v) => v?.toLocaleString() },
    { title: 'Lương chính', dataIndex: 'luong_chinh', width: 110,
      render: (v) => v?.toLocaleString() },
    { title: 'Lương dạy', dataIndex: 'luong_day', width: 110,
      render: (v) => v?.toLocaleString() },
    { title: 'L. Hiệu quả', dataIndex: 'luong_hieu_qua', width
