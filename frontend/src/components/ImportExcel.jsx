import React, { useState } from 'react';
import {
  Modal,
  Upload,
  Button,
  Alert,
  List,
  Typography,
  Space,
  Progress,
  Descriptions,
} from 'antd';
import {
  InboxOutlined,
  DownloadOutlined,
  FileExcelOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';

const { Dragger } = Upload;
const { Text, Title } = Typography;

const MAX_ERRORS_DISPLAY = 100;
const PREVIEW_ROWS = 20;

/**
 * Reusable Excel/CSV import modal component.
 *
 * Props:
 * - title: string - Modal title
 * - open: boolean - Modal visibility
 * - onClose: () => void - Close handler
 * - onConfirm: (file: File) => Promise<{ imported_count?, errors?, preview? }> - Upload handler
 * - accept: string - Accepted file types (default: '.xlsx,.xls,.csv')
 * - maxSize: number - Max file size in MB (default: 10)
 * - templateUrl: string? - Optional URL to download import template
 */
export default function ImportExcel({
  title = 'Import Excel',
  open = false,
  onClose,
  onConfirm,
  accept = '.xlsx,.xls,.csv',
  maxSize = 10,
  templateUrl,
}) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { imported_count, errors, preview }
  const [fileError, setFileError] = useState(null);

  const resetState = () => {
    setFile(null);
    setLoading(false);
    setResult(null);
    setFileError(null);
  };

  const handleClose = () => {
    resetState();
    onClose?.();
  };

  const validateFile = (f) => {
    // Check file size
    const sizeMB = f.size / (1024 * 1024);
    if (sizeMB > maxSize) {
      return `File vượt quá dung lượng cho phép (tối đa ${maxSize}MB). File hiện tại: ${sizeMB.toFixed(2)}MB`;
    }

    // Check file extension
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
    const allowedExts = accept.split(',').map((e) => e.trim().toLowerCase());
    if (!allowedExts.includes(ext)) {
      return `Định dạng file không hợp lệ. Chỉ chấp nhận: ${accept}`;
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
    }
    // Prevent auto upload
    return false;
  };

  const handleRemove = () => {
    setFile(null);
    setFileError(null);
    setResult(null);
  };

  const handleConfirm = async () => {
    if (!file || !onConfirm) return;

    setLoading(true);
    setResult(null);
    try {
      const res = await onConfirm(file);
      setResult(res);
      // If no errors, close after a brief display
      if (!res?.errors?.length) {
        // Success - keep modal open to show summary
      }
    } catch (e) {
      const errData = e.response?.data;
      if (errData?.errors) {
        setResult(errData);
      } else {
        setResult({
          errors: [{ row: 0, message: errData?.detail || 'Lỗi khi import file' }],
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const hasErrors = result?.errors?.length > 0;
  const isSuccess = result && !hasErrors;

  const renderUploadArea = () => (
    <div>
      <Dragger
        accept={accept}
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
          Kéo thả file vào đây hoặc bấm để chọn file
        </p>
        <p className="ant-upload-hint">
          Hỗ trợ: {accept} (tối đa {maxSize}MB)
        </p>
      </Dragger>

      {fileError && (
        <Alert
          type="error"
          message={fileError}
          showIcon
          style={{ marginTop: 12 }}
        />
      )}

      {file && !fileError && (
        <Descriptions
          size="small"
          column={2}
          style={{ marginTop: 12 }}
          bordered
        >
          <Descriptions.Item label="Tên file">
            <Space>
              <FileExcelOutlined style={{ color: '#52c41a' }} />
              <Text>{file.name}</Text>
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Kích thước">
            {formatFileSize(file.size)}
          </Descriptions.Item>
        </Descriptions>
      )}

      {templateUrl && (
        <div style={{ marginTop: 12 }}>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            href={templateUrl}
            target="_blank"
            size="small"
          >
            Tải file mẫu
          </Button>
        </div>
      )}
    </div>
  );

  const renderResult = () => {
    if (!result) return null;

    if (isSuccess) {
      return (
        <div style={{ marginTop: 16 }}>
          <Alert
            type="success"
            icon={<CheckCircleOutlined />}
            message="Import thành công"
            description={
              result.imported_count != null
                ? `Đã import ${result.imported_count} dòng dữ liệu.`
                : 'Dữ liệu đã được import thành công.'
            }
            showIcon
          />
          {result.preview?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <Text type="secondary">
                Xem trước {Math.min(result.preview.length, PREVIEW_ROWS)} /{' '}
                {result.total_count || result.preview.length} dòng
              </Text>
            </div>
          )}
        </div>
      );
    }

    if (hasErrors) {
      const errorsToShow = result.errors.slice(0, MAX_ERRORS_DISPLAY);
      const totalErrors = result.errors.length;

      return (
        <div style={{ marginTop: 16 }}>
          <Alert
            type="error"
            icon={<CloseCircleOutlined />}
            message="Import có lỗi"
            description={`Phát hiện ${totalErrors} lỗi. ${
              totalErrors > MAX_ERRORS_DISPLAY
                ? `Hiển thị ${MAX_ERRORS_DISPLAY} lỗi đầu tiên.`
                : ''
            }`}
            showIcon
            style={{ marginBottom: 12 }}
          />
          {result.imported_count != null && result.imported_count > 0 && (
            <Alert
              type="warning"
              message={`Đã import ${result.imported_count} dòng hợp lệ. Các dòng lỗi bị bỏ qua.`}
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
                <List.Item style={{ padding: '6px 12px' }}>
                  <Text type="danger">
                    {err.row > 0 && <Text strong>Dòng {err.row}: </Text>}
                    {err.message || err.error || JSON.stringify(err)}
                  </Text>
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
    if (isSuccess) {
      return [
        <Button key="close" type="primary" onClick={handleClose}>
          Đóng
        </Button>,
      ];
    }

    return [
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
        Xác nhận
      </Button>,
    ];
  };

  return (
    <Modal
      title={title}
      open={open}
      onCancel={handleClose}
      footer={renderFooter()}
      width={640}
      destroyOnClose
      maskClosable={!loading}
      closable={!loading}
    >
      {loading && (
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <Progress percent={99} status="active" showInfo={false} />
          <Text type="secondary">Đang xử lý file...</Text>
        </div>
      )}

      {renderUploadArea()}
      {renderResult()}
    </Modal>
  );
}
