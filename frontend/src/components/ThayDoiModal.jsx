import React, { useState, useEffect, useCallback } from 'react';
import {
  Modal,
  Form,
  Select,
  DatePicker,
  InputNumber,
  Input,
  Alert,
  message,
  Tabs,
  Button,
  Space,
} from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';
import ImportExcel from './ImportExcel';

const { TextArea } = Input;

/**
 * ThayDoiModal — Modal for creating/importing teacher substitution change records.
 *
 * Props:
 * - open: boolean — modal visibility
 * - onClose: () => void — close handler
 * - onSuccess: () => void — callback after successful create/import
 * - thang: number — current month context
 * - nam: number — current year context
 */
export default function ThayDoiModal({ open, onClose, onSuccess, thang, nam }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [duplicateWarning, setDuplicateWarning] = useState(null);
  const [activeTab, setActiveTab] = useState('single');
  const [importOpen, setImportOpen] = useState(false);

  // Dropdown data
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);

  const fetchDropdowns = useCallback(async () => {
    try {
      const [teacherRes, subjectRes, classRes] = await Promise.all([
        api.get('/nhan-vien', { params: { nhom_nv: 'GV' } }),
        api.get('/danh-muc/mon-hoc'),
        api.get('/danh-muc/lop'),
      ]);
      setTeachers(teacherRes.data);
      setSubjects(subjectRes.data);
      setClasses(classRes.data);
    } catch {
      // Silent fail for dropdowns
    }
  }, []);

  useEffect(() => {
    if (open) {
      fetchDropdowns();
      setDuplicateWarning(null);
      setActiveTab('single');
    }
  }, [open, fetchDropdowns]);

  const handleClose = () => {
    form.resetFields();
    setDuplicateWarning(null);
    setLoading(false);
    onClose?.();
  };

  // Check for duplicate before submit
  const checkDuplicate = async (values) => {
    try {
      const res = await api.get(`/tkb/thay-doi/${thang}/${nam}`);
      const existing = res.data;
      const ngayStr = values.ngay.format('YYYY-MM-DD');
      const dup = existing.find(
        (r) =>
          r.gv_goc_id === values.gv_goc_id &&
          r.ngay === ngayStr &&
          r.tiet === values.tiet &&
          r.lop_id === values.lop_id
      );
      return dup;
    } catch {
      return null;
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    setDuplicateWarning(null);

    // Check for duplicate locally
    const dup = await checkDuplicate(values);
    if (dup) {
      const teacherName = teachers.find((t) => t.id === values.gv_goc_id)?.ho_ten || '';
      const className = classes.find((c) => c.id === values.lop_id)?.ten || '';
      setDuplicateWarning(
        `Đã tồn tại bản ghi: GV "${teacherName}", ngày ${values.ngay.format('DD/MM/YYYY')}, tiết ${values.tiet}, lớp "${className}". Bản ghi có thể bị trùng.`
      );
      setLoading(false);
      return;
    }

    try {
      const payload = {
        gv_goc_id: values.gv_goc_id,
        gv_thay_id: values.gv_thay_id,
        ngay: values.ngay.format('YYYY-MM-DD'),
        tiet: values.tiet,
        lop_id: values.lop_id,
        mon_hoc_id: values.mon_hoc_id,
        ly_do: values.ly_do || null,
        thang,
        nam,
      };

      const res = await api.post('/tkb/thay-doi', payload);

      // Handle warning response (GV not in TKB)
      if (res.data?.warning) {
        message.warning(res.data.message);
      } else {
        message.success('Thêm thay đổi thành công');
      }

      form.resetFields();
      setDuplicateWarning(null);
      onSuccess?.();
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (e.response?.status === 409) {
        // Duplicate from backend
        setDuplicateWarning(typeof detail === 'string' ? detail : 'Bản ghi đã tồn tại (trùng lặp).');
      } else {
        message.error(typeof detail === 'string' ? detail : 'Lỗi khi thêm thay đổi');
      }
    } finally {
      setLoading(false);
    }
  };

  // Force submit even if duplicate warning is shown
  const handleForceSubmit = async () => {
    setDuplicateWarning(null);
    const values = form.getFieldsValue();
    setLoading(true);
    try {
      const payload = {
        gv_goc_id: values.gv_goc_id,
        gv_thay_id: values.gv_thay_id,
        ngay: values.ngay.format('YYYY-MM-DD'),
        tiet: values.tiet,
        lop_id: values.lop_id,
        mon_hoc_id: values.mon_hoc_id,
        ly_do: values.ly_do || null,
        thang,
        nam,
      };

      const res = await api.post('/tkb/thay-doi', payload);
      if (res.data?.warning) {
        message.warning(res.data.message);
      } else {
        message.success('Thêm thay đổi thành công');
      }
      form.resetFields();
      onSuccess?.();
    } catch (e) {
      const detail = e.response?.data?.detail;
      message.error(typeof detail === 'string' ? detail : 'Lỗi khi thêm thay đổi');
    } finally {
      setLoading(false);
    }
  };

  // Bulk import handler
  const handleBulkImport = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thang', thang);
    formData.append('nam', nam);

    // Parse the file client-side or send as JSON
    // For this API, we need to parse Excel/CSV and send JSON payload
    // We'll use the import endpoint which accepts List[ThayDoiCreate]
    const res = await api.post('/tkb/thay-doi/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  };

  const handleImportSuccess = (result) => {
    if (!result?.errors?.length) {
      message.success(`Import thành công ${result?.imported_count || ''} bản ghi`);
      setImportOpen(false);
      onSuccess?.();
    }
  };

  const renderSingleForm = () => (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{ tiet: 1 }}
    >
      {duplicateWarning && (
        <Alert
          type="warning"
          message="Cảnh báo trùng lặp"
          description={
            <div>
              <p>{duplicateWarning}</p>
              <Space>
                <Button size="small" onClick={() => setDuplicateWarning(null)}>
                  Sửa lại
                </Button>
                <Button size="small" type="primary" onClick={handleForceSubmit} loading={loading}>
                  Vẫn thêm
                </Button>
              </Space>
            </div>
          }
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Form.Item
        name="gv_goc_id"
        label="Giáo viên gốc"
        rules={[{ required: true, message: 'Vui lòng chọn giáo viên gốc' }]}
      >
        <Select
          showSearch
          placeholder="Chọn giáo viên gốc"
          optionFilterProp="children"
          filterOption={(input, option) =>
            option.children.toLowerCase().includes(input.toLowerCase())
          }
        >
          {teachers.map((t) => (
            <Select.Option key={t.id} value={t.id}>
              {t.ho_ten}{t.ten_goi ? ` (${t.ten_goi})` : ''} - {t.ma_nv}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="gv_thay_id"
        label="Giáo viên dạy thay"
        rules={[{ required: true, message: 'Vui lòng chọn giáo viên dạy thay' }]}
      >
        <Select
          showSearch
          placeholder="Chọn giáo viên dạy thay"
          optionFilterProp="children"
          filterOption={(input, option) =>
            option.children.toLowerCase().includes(input.toLowerCase())
          }
        >
          {teachers.map((t) => (
            <Select.Option key={t.id} value={t.id}>
              {t.ho_ten}{t.ten_goi ? ` (${t.ten_goi})` : ''} - {t.ma_nv}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="ngay"
        label="Ngày"
        rules={[{ required: true, message: 'Vui lòng chọn ngày' }]}
      >
        <DatePicker
          format="DD/MM/YYYY"
          style={{ width: '100%' }}
          placeholder="Chọn ngày"
          // Default to current month context
          defaultPickerValue={dayjs(`${nam}-${String(thang).padStart(2, '0')}-01`)}
        />
      </Form.Item>

      <Form.Item
        name="tiet"
        label="Tiết"
        rules={[{ required: true, message: 'Vui lòng nhập tiết (1-10)' }]}
      >
        <InputNumber min={1} max={10} style={{ width: '100%' }} placeholder="1-10" />
      </Form.Item>

      <Form.Item
        name="lop_id"
        label="Lớp"
        rules={[{ required: true, message: 'Vui lòng chọn lớp' }]}
      >
        <Select
          showSearch
          placeholder="Chọn lớp"
          optionFilterProp="children"
          filterOption={(input, option) =>
            option.children.toLowerCase().includes(input.toLowerCase())
          }
        >
          {classes.map((c) => (
            <Select.Option key={c.id} value={c.id}>
              {c.ten}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="mon_hoc_id"
        label="Môn học"
        rules={[{ required: true, message: 'Vui lòng chọn môn học' }]}
      >
        <Select
          showSearch
          placeholder="Chọn môn học"
          optionFilterProp="children"
          filterOption={(input, option) =>
            option.children.toLowerCase().includes(input.toLowerCase())
          }
        >
          {subjects.map((s) => (
            <Select.Option key={s.id} value={s.id}>
              {s.ten}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="ly_do"
        label="Lý do"
        rules={[{ max: 200, message: 'Lý do tối đa 200 ký tự' }]}
      >
        <TextArea
          rows={2}
          maxLength={200}
          showCount
          placeholder="Nhập lý do thay đổi (không bắt buộc)"
        />
      </Form.Item>
    </Form>
  );

  const renderBulkImport = () => (
    <div>
      <Alert
        type="info"
        message="Import hàng loạt"
        description={
          <span>
            Tải lên file Excel/CSV chứa danh sách thay đổi người dạy.
            Tối đa 500 dòng mỗi lần import. Nếu có bất kỳ dòng nào lỗi, toàn bộ sẽ bị từ chối.
          </span>
        }
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Button
        type="primary"
        icon={<UploadOutlined />}
        onClick={() => setImportOpen(true)}
      >
        Chọn file import
      </Button>

      <ImportExcel
        title="Import thay đổi người dạy"
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleBulkImport}
        accept=".xlsx,.xls,.csv"
        maxSize={10}
      />
    </div>
  );

  const tabItems = [
    {
      key: 'single',
      label: 'Thêm đơn lẻ',
      children: renderSingleForm(),
    },
    {
      key: 'bulk',
      label: 'Import hàng loạt',
      children: renderBulkImport(),
    },
  ];

  const handleOk = () => {
    if (activeTab === 'single') {
      form.submit();
    }
    // Bulk import is handled via its own modal
  };

  return (
    <Modal
      title="Thay đổi người dạy"
      open={open}
      onCancel={handleClose}
      onOk={handleOk}
      okText={activeTab === 'single' ? 'Thêm' : undefined}
      okButtonProps={{
        loading,
        style: activeTab === 'bulk' ? { display: 'none' } : {},
      }}
      cancelText="Đóng"
      width={600}
      destroyOnClose
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />
    </Modal>
  );
}
