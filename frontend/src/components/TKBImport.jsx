import React, { useState, useCallback } from 'react';
import {
  Modal,
  Upload,
  Button,
  Alert,
  List,
  Typography,
  Space,
  Popconfirm,
  Tag,
  Divider,
  Spin,
} from 'antd';
import {
  InboxOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import api from '../services/api';

const { Dragger } = Upload;
const { Text } = Typography;

const MAX_FILE_SIZE_MB = 10;
const ACCEPTED_FORMATS = '.xlsx,.xls,.csv';
const MAX_ERRORS_DISPLAY = 100;

/**
 * TKBImport - Timetable Import Modal with TKB-specific logic.
 *
 * Props:
 * - open: boolean - Modal visibility
 * - onClose: () => void - Close handler
 * - onSuccess: (result) => void - Called after successful import
 * - thang: number - Month for import context
 * - nam: number - Year for import context
 */
export default function TKBImport({ open, onClose, onSuccess, thang, nam }) {
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [conflictMode, setConflictMode] = useState(false);

  const resetState = useCallback(() => {
    setFile(null);
    setFileError(null);
    setLoading(false);
    setResult(null);
    setConflictMode(false);
  }, []);

  const handleClose = () => {
    resetState();
    onClose?.();
  };

  const validateFile = (f) => {
    const sizeMB = f.size / (1024 * 1024);
    if (sizeMB > MAX_FILE_SIZE_MB) {
      return `File vượt quá dung lượng cho phép (tối đa ${MAX_FILE_SIZE_MB}MB). File hiện tại: ${sizeMB.toFixed(2)}MB`;
    }
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
    const allowedExts = ACCEPTED_FORMATS.split(',').map((e) => e.trim().toLowerCase());
    if (!allowedExts.includes(ext)) {
      return `Định dạng file không hợp lệ. Chỉ chấp nhận: ${ACCEPTED_FORMATS}`;
    }
    return null;
  };

  const handleBeforeUpload = (f) => {
    const error = validateFile(f);
    if (error) {
      setFileError(error);
      setFile(null);
    } else {
      setFileError(null);
      setFile(f);
      setResult(null);
      setConflictMode(false);
    }
    return false;
  };

  const handleRemove = () => {
    setFile(null);
    setFileError(null);
    setResult(null);
    setConflictMode(false);
  };

  const parseCSV = (text) => {
    const lines = text.trim().split(/\r?\n/);
    if (lines.length < 2) return [];

    const header = lines[0].split(',').map((h) => h.trim().toLowerCase().replace(/['"]/g, ''));
    const rows = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map((v) => v.trim().replace(/['"]/g, ''));
      if (values.length === 0 || (values.length === 1 && !values[0])) continue;

      const row = {};
      header.forEach((col, idx) => {
        row[col] = values[idx] || '';
      });

      rows.push({
        giao_vien: row['giao_vien'] || row['giáo viên'] || row['gv'] || '',
        mon_hoc: row['mon_hoc'] || row['môn học'] || row['mon'] || '',
        khoi: row['khoi'] || row['khối'] || '',
        lop: row['lop'] || row['lớp'] || '',
        so_tiet: parseInt(row['so_tiet'] || row['số tiết'] || '0', 10) || 0,
        loai_tiet: row['loai_tiet'] || row['loại tiết'] || 'chinh_khoa',
      });
    }
    return rows;
  };

  const readFileAsText = (f) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Không thể đọc file'));
      reader.readAsText(f);
    });
  };

  const doImport = async (replaceExisting = false) => {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setConflictMode(false);

    try {
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      let rows = [];

      if (ext === '.csv') {
        const text = await readFileAsText(file);
        rows = parseCSV(text);
      } else {
        // For Excel files (.xlsx, .xls), send as FormData
        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await api.post(
            `/tkb/import?thang=${thang}&nam=${nam}${replaceExisting ? '&replace=true' : ''}`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );
          setResult(response.data);
          if (!response.data.errors?.length && response.data.imported_count > 0) {
            onSuccess?.(response.data);
          }
          return;
        } catch (err) {
          if (err.response?.status === 409) {
            setConflictMode(true);
            return;
          }
          // If multipart not supported, try reading as text (for CSV-like xlsx)
          const errData = err.response?.data;
          if (errData?.errors) {
            setResult(errData);
          } else {
            setResult({
              errors: [{
                row: 0,
                message: errData?.detail || 'File Excel không thể xử lý. Vui lòng chuyển sang định dạng CSV.',
              }],
            });
          }
          return;
        } finally {
          setLoading(false);
        }
      }

      if (rows.length === 0) {
        setResult({ errors: [{ row: 0, message: 'File không có dữ liệu hợp lệ' }] });
        return;
      }

      // Send parsed rows as JSON
      const payload = {
        thang,
        nam,
        replace_existing: replaceExisting,
        rows,
      };

      const response = await api.post('/tkb/import', payload);
      const data = response.data;
      setResult(data);

      // Notify parent on successful import (even partial)
      if (data.imported_count > 0) {
        onSuccess?.(data);
      }
    } catch (err) {
      if (err.response?.status === 409) {
        setConflictMode(true);
      } else {
        const errData = err.response?.data;
        if (errData?.errors) {
          setResult(errData);
        } else {
          setResult({
            errors: [{ row: 0, message: errData?.detail || 'Lỗi khi import file' }],
          });
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => doImport(false);
  const handleReplaceConfirm = () => doImport(true);

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/tkb/template');
      const templateInfo = response.data;
      const columns = templateInfo.columns.map((c) => c.name);
      const descriptions = templateInfo.columns.map((c) => c.description);
      const csvContent = columns.join(',') + '\n' + descriptions.join(',') + '\n';
      downloadCSV(csvContent, 'mau_tkb_import.csv');
    } catch {
      const csvContent = 'giao_vien,mon_hoc,khoi,lop,so_tiet,loai_tiet\n';
      downloadCSV(csvContent, 'mau_tkb_import.csv');
    }
  };

  const downloadCSV = (content, filename) => {
    const blob = new Blob(['\uFEFF' + content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const hasErrors = result?.errors?.length > 0;
  const isSuccess = result && !hasErrors && result.imported_count > 0;
  const hasPartialSuccess = hasErrors && result?.imported_count > 0;

  // ─── Render Functions ──────────────────────────────────────────────

  const renderUploadArea = () => (
    <div>
      <Dragger
        accept={ACCEPTED_FORMATS}
        beforeUpload={handleBeforeUpload}
        onRemove={handleRemove}
        fileList={file ? [file] : []}
        maxCount={1}
        disabled={loading}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">
          Kéo thả file TKB vào đây hoặc bấm để chọn file
        </p>
        <p className="ant-upload-hint">
          Hỗ trợ: Excel (.xlsx, .xls) và CSV (tối đa {MAX_FILE_SIZE_MB}MB)
        </p>
      </Dragger>

      {fileError && (
        <Alert type="error" message={fileError} showIcon style={{ marginTop: 12 }} />
      )}

      {thang && nam && !result && (
        <Alert
          type="info"
          message={`Import TKB cho tháng ${thang}/${nam}`}
          style={{ marginTop: 12 }}
          showIcon
        />
      )}
    </div>
  );

  const renderConflictWarning = () => {
    if (!conflictMode) return null;
    return (
      <Alert
        type="warning"
        icon={<WarningOutlined />}
        message={`Dữ liệu TKB tháng ${thang}/${nam} đã tồn tại`}
        description="Bạn có muốn ghi đè dữ liệu hiện tại? Thao tác này không thể hoàn tác."
        showIcon
        style={{ marginTop: 16 }}
        action={
          <Space direction="vertical" size="small">
            <Popconfirm
              title="Xác nhận ghi đè?"
              description="Dữ liệu TKB cũ sẽ bị xóa và thay thế bằng dữ liệu mới."
              onConfirm={handleReplaceConfirm}
              okText="Ghi đè"
              cancelText="Hủy"
              okButtonProps={{ danger: true }}
            >
              <Button danger size="small" loading={loading}>
                Ghi đè
              </Button>
            </Popconfirm>
            <Button size="small" onClick={() => setConflictMode(false)}>
              Hủy bỏ
            </Button>
          </Space>
        }
      />
    );
  };

  const renderResult = () => {
    if (!result) return null;

    if (isSuccess) {
      return (
        <div style={{ marginTop: 16 }}>
          <Alert
            type="success"
            icon={<CheckCircleOutlined />}
            message="Import TKB thành công"
            description={`Đã import ${result.imported_count}/${result.total_rows || result.imported_count} dòng dữ liệu cho tháng ${thang}/${nam}.`}
            showIcon
          />
        </div>
      );
    }

    if (hasErrors) {
      const errorsToShow = result.errors.slice(0, MAX_ERRORS_DISPLAY);
      const totalErrors = result.errors.length;

      return (
        <div style={{ marginTop: 16 }}>
          {hasPartialSuccess ? (
            <Alert
              type="warning"
              icon={<WarningOutlined />}
              message="Import hoàn tất với một số lỗi"
              description={`Đã import ${result.imported_count} dòng hợp lệ. ${totalErrors} dòng có lỗi đã bị bỏ qua.`}
              showIcon
              style={{ marginBottom: 12 }}
            />
          ) : (
            <Alert
              type="error"
              icon={<CloseCircleOutlined />}
              message="Import thất bại"
              description={`${totalErrors} lỗi được phát hiện. Không có dòng nào được import.${totalErrors > MAX_ERRORS_DISPLAY ? ` Hiển thị ${MAX_ERRORS_DISPLAY} lỗi đầu tiên.` : ''}`}
              showIcon
              style={{ marginBottom: 12 }}
            />
          )}

          <div
            style={{
              maxHeight: 300,
              overflowY: 'auto',
              border: '1px solid #f0f0f0',
              borderRadius: 6,
            }}
          >
            <List
              size="small"
              dataSource={errorsToShow}
              renderItem={(err) => (
                <List.Item style={{ padding: '8px 12px' }}>
                  <Space direction="vertical" size={0} style={{ width: '100%' }}>
                    <Space wrap>
                      {err.row > 0 && <Tag color="red">Dòng {err.row}</Tag>}
                      {err.field && <Tag color="orange">Cột: {err.field}</Tag>}
                      {err.value && (
                        <Tag color="volcano">Giá trị: {err.value}</Tag>
                      )}
                    </Space>
                    <Text type="danger" style={{ fontSize: 13 }}>
                      {err.message || err.error || JSON.stringify(err)}
                    </Text>
                  </Space>
                </List.Item>
              )}
            />
          </div>

          {totalErrors > MAX_ERRORS_DISPLAY && (
            <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
              ... và {totalErrors - MAX_ERRORS_DISPLAY} lỗi khác
            </Text>
          )}
        </div>
      );
    }

    return null;
  };

  const renderFooter = () => {
    // Success or partial success with import already done
    if (isSuccess || hasPartialSuccess) {
      return [
        <Button key="close" type="primary" onClick={handleClose}>
          Đóng
        </Button>,
      ];
    }

    // Errors only, no rows imported — user can cancel
    if (hasErrors && !hasPartialSuccess) {
      return [
        <Button key="cancel" onClick={handleClose}>
          Hủy bỏ
        </Button>,
        <Button
          key="import-valid"
          type="primary"
          onClick={handleConfirm}
          loading={loading}
          disabled={!file}
          title="Bỏ qua dòng lỗi và chỉ import dòng hợp lệ"
        >
          Import dòng hợp lệ
        </Button>,
      ];
    }

    // Default: template download + cancel + import
    return [
      <Button
        key="template"
        icon={<DownloadOutlined />}
        onClick={handleDownloadTemplate}
        style={{ marginRight: 'auto' }}
      >
        Tải file mẫu
      </Button>,
      <Button key="cancel" onClick={handleClose} disabled={loading}>
        Hủy
      </Button>,
      <Button
        key="confirm"
        type="primary"
        onClick={handleConfirm}
        loading={loading}
        disabled={!file || !!fileError}
      >
        Import
      </Button>,
    ];
  };

  return (
    <Modal
      title={
        <Space>
          <ExclamationCircleOutlined style={{ color: '#1890ff' }} />
          <span>Import Thời khóa biểu</span>
        </Space>
      }
      open={open}
      onCancel={handleClose}
      footer={renderFooter()}
      width={700}
      destroyOnClose
      maskClosable={!loading}
      closable={!loading}
    >
      {loading && (
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <Spin tip="Đang xử lý file..." />
        </div>
      )}

      {renderUploadArea()}
      {renderConflictWarning()}
      {renderResult()}

      {!result && !conflictMode && (
        <div style={{ marginTop: 16 }}>
          <Divider style={{ margin: '12px 0' }} />
          <Space>
            <Button
              icon={<DownloadOutlined />}
              size="small"
              onClick={handleDownloadTemplate}
            >
              Tải file mẫu
            </Button>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Cột: giao_vien, mon_hoc, khoi, lop, so_tiet, loai_tiet
            </Text>
          </Space>
        </div>
      )}
    </Modal>
  );
}
