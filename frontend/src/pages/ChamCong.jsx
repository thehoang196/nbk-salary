import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Space, DatePicker, message, Card, Typography,
  InputNumber, Tag, Upload, Form, Tooltip,
} from 'antd';
import {
  UploadOutlined, SaveOutlined, ReloadOutlined,
  CheckCircleOutlined, WarningOutlined, ExclamationCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';

const { Title } = Typography;

/**
 * ChamCong Page - VP Attendance Management
 *
 * Features:
 * - Editable grid showing VP employees with attendance summary columns
 * - Columns: Nhân viên, Ngày công, Ngày nghỉ, Ngày phép, Làm thêm, Trạng thái
 * - Editable cells for ngay_cong, ngay_nghi, ngay_phep, lam_them
 * - Visual flagging: yellow for incomplete (ngay_cong < cong_chuan), red for very low
 * - Misa import support
 * - Inline save via PUT /api/cham-cong/tong-hop/{id}
 *
 * Requirements: 8.8 (manual edit), 8.9 (flag incomplete records)
 */
export default function ChamCong() {
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [employees, setEmployees] = useState([]);
  const [editedRows, setEditedRows] = useState({}); // { id: { field: value } }
  const [savingIds, setSavingIds] = useState(new Set());

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch attendance summary (tổng hợp công)
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/cham-cong/tong-hop/${thang}/${nam}`);
      setData(res.data || []);
      setEditedRows({});
    } catch (e) {
      if (e.response?.status !== 404) {
        message.error('Lỗi tải dữ liệu chấm công');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  // Fetch VP employees
  const fetchEmployees = useCallback(async () => {
    try {
      const res = await api.get('/nhan-vien');
      const list = res.data?.items || res.data || [];
      // Filter VP employees only
      setEmployees(list.filter((nv) => nv.nhom_nv === 'VP'));
    } catch {
      setEmployees([]);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  // Build employee name map
  const employeeMap = {};
  employees.forEach((nv) => {
    employeeMap[nv.id] = nv;
  });

  // Handle inline cell edit
  const handleCellChange = (recordId, field, value) => {
    setEditedRows((prev) => ({
      ...prev,
      [recordId]: {
        ...(prev[recordId] || {}),
        [field]: value,
      },
    }));
  };

  // Get current value (edited or original)
  const getCellValue = (record, field) => {
    if (editedRows[record.id] && editedRows[record.id][field] !== undefined) {
      return editedRows[record.id][field];
    }
    return record[field];
  };

  // Save a single row
  const handleSaveRow = async (record) => {
    const edits = editedRows[record.id];
    if (!edits) return;

    setSavingIds((prev) => new Set([...prev, record.id]));
    try {
      const payload = {
        ngay_cong: edits.ngay_cong !== undefined ? edits.ngay_cong : record.ngay_cong,
        ngay_nghi: edits.ngay_nghi !== undefined ? edits.ngay_nghi : record.ngay_nghi,
        ngay_phep: edits.ngay_phep !== undefined ? edits.ngay_phep : record.ngay_phep,
        lam_them: edits.lam_them !== undefined ? edits.lam_them : record.lam_them,
      };

      await api.put(`/cham-cong/tong-hop/${record.id}`, payload);
      message.success('Đã lưu');

      // Clear edited state for this row and update data
      setEditedRows((prev) => {
        const copy = { ...prev };
        delete copy[record.id];
        return copy;
      });

      // Update local data
      setData((prev) =>
        prev.map((r) => (r.id === record.id ? { ...r, ...payload } : r))
      );
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi khi lưu');
    } finally {
      setSavingIds((prev) => {
        const copy = new Set(prev);
        copy.delete(record.id);
        return copy;
      });
    }
  };

  // Save all edited rows
  const handleSaveAll = async () => {
    const editedIds = Object.keys(editedRows).map(Number);
    if (editedIds.length === 0) {
      message.info('Không có thay đổi');
      return;
    }

    for (const id of editedIds) {
      const record = data.find((r) => r.id === id);
      if (record) {
        await handleSaveRow(record);
      }
    }
  };

  // Misa import handler
  const handleMisaImport = async (info) => {
    const file = info.file;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('thang', thang);
    formData.append('nam', nam);

    try {
      const res = await api.post('/cham-cong/import-misa', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const result = res.data;
      if (result.errors?.length > 0) {
        message.warning(`Đã import ${result.imported_count}/${result.total_rows} dòng. ${result.errors.length} lỗi.`);
      } else {
        message.success(`Đã import ${result.imported_count} dòng thành công`);
      }
      fetchData();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi import Misa');
    }
  };

  // Determine row status and highlight class
  const getRowStatus = (record) => {
    const ngayCong = getCellValue(record, 'ngay_cong');
    const congChuan = record.cong_chuan || 26;

    if (ngayCong < congChuan * 0.5) {
      return 'critical'; // Very low - red
    }
    if (ngayCong < congChuan) {
      return 'incomplete'; // Below standard - yellow
    }
    return 'complete';
  };

  // Render status tag
  const renderStatus = (record) => {
    const status = getRowStatus(record);
    const ngayCong = getCellValue(record, 'ngay_cong');
    const congChuan = record.cong_chuan || 26;

    if (record.is_confirmed) {
      return (
        <Tag icon={<CheckCircleOutlined />} color="success">
          Đã xác nhận
        </Tag>
      );
    }

    if (status === 'critical') {
      return (
        <Tooltip title={`Ngày công (${ngayCong}) rất thấp so với chuẩn (${congChuan})`}>
          <Tag icon={<ExclamationCircleOutlined />} color="error">
            Thiếu nhiều
          </Tag>
        </Tooltip>
      );
    }

    if (status === 'incomplete') {
      return (
        <Tooltip title={`Ngày công (${ngayCong}) < công chuẩn (${congChuan})`}>
          <Tag icon={<WarningOutlined />} color="warning">
            Chưa đủ
          </Tag>
        </Tooltip>
      );
    }

    return <Tag color="default">Đủ công</Tag>;
  };

  // Editable number cell renderer
  const renderEditableCell = (record, field) => {
    const value = getCellValue(record, field);
    const isEdited = editedRows[record.id] && editedRows[record.id][field] !== undefined;

    return (
      <InputNumber
        size="small"
        min={0}
        max={31}
        step={0.5}
        precision={1}
        value={value}
        onChange={(val) => handleCellChange(record.id, field, val)}
        style={{
          width: 70,
          borderColor: isEdited ? '#1890ff' : undefined,
          backgroundColor: isEdited ? '#e6f7ff' : undefined,
        }}
      />
    );
  };

  // Table columns
  const columns = [
    {
      title: 'Nhân viên',
      dataIndex: 'nhan_vien_id',
      key: 'nhan_vien',
      fixed: 'left',
      width: 180,
      render: (id) => {
        const nv = employeeMap[id];
        return nv ? `${nv.ho_ten}${nv.ma_nv ? ` (${nv.ma_nv})` : ''}` : `NV #${id}`;
      },
      sorter: (a, b) => {
        const nameA = employeeMap[a.nhan_vien_id]?.ho_ten || '';
        const nameB = employeeMap[b.nhan_vien_id]?.ho_ten || '';
        return nameA.localeCompare(nameB);
      },
    },
    {
      title: 'Ngày công',
      dataIndex: 'ngay_cong',
      key: 'ngay_cong',
      width: 110,
      align: 'center',
      render: (_, record) => renderEditableCell(record, 'ngay_cong'),
    },
    {
      title: 'Ngày nghỉ',
      dataIndex: 'ngay_nghi',
      key: 'ngay_nghi',
      width: 110,
      align: 'center',
      render: (_, record) => renderEditableCell(record, 'ngay_nghi'),
    },
    {
      title: 'Ngày phép',
      dataIndex: 'ngay_phep',
      key: 'ngay_phep',
      width: 110,
      align: 'center',
      render: (_, record) => renderEditableCell(record, 'ngay_phep'),
    },
    {
      title: 'Làm thêm',
      dataIndex: 'lam_them',
      key: 'lam_them',
      width: 110,
      align: 'center',
      render: (_, record) => renderEditableCell(record, 'lam_them'),
    },
    {
      title: 'Công chuẩn',
      dataIndex: 'cong_chuan',
      key: 'cong_chuan',
      width: 100,
      align: 'center',
      render: (val) => val || 26,
    },
    {
      title: 'Trạng thái',
      key: 'trang_thai',
      width: 140,
      align: 'center',
      render: (_, record) => renderStatus(record),
    },
    {
      title: '',
      key: 'actions',
      width: 70,
      align: 'center',
      render: (_, record) => {
        const hasEdits = !!editedRows[record.id];
        return hasEdits ? (
          <Button
            type="primary"
            size="small"
            icon={<SaveOutlined />}
            loading={savingIds.has(record.id)}
            onClick={() => handleSaveRow(record)}
          />
        ) : null;
      },
    },
  ];

  // Row class based on status
  const getRowClassName = (record) => {
    const status = getRowStatus(record);
    if (status === 'critical') return 'attendance-row-critical';
    if (status === 'incomplete') return 'attendance-row-incomplete';
    return '';
  };

  const hasEdits = Object.keys(editedRows).length > 0;

  return (
    <div>
      <Title level={4}>Chấm công VP (Khối văn phòng)</Title>

      {/* Controls */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <span>Tháng:</span>
          <DatePicker
            picker="month"
            value={selectedMonth}
            onChange={(date) => date && setSelectedMonth(date)}
            format="MM/YYYY"
            allowClear={false}
          />
          <Upload
            accept=".xlsx,.xls,.csv"
            showUploadList={false}
            customRequest={handleMisaImport}
          >
            <Button icon={<UploadOutlined />}>Import Misa</Button>
          </Upload>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchData}
          >
            Tải lại
          </Button>
          {hasEdits && (
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveAll}
            >
              Lưu tất cả ({Object.keys(editedRows).length})
            </Button>
          )}
        </Space>
      </Card>

      {/* Inline styles for row highlighting */}
      <style>{`
        .attendance-row-incomplete {
          background-color: #fffbe6 !important;
        }
        .attendance-row-incomplete:hover > td {
          background-color: #fff7cc !important;
        }
        .attendance-row-critical {
          background-color: #fff1f0 !important;
        }
        .attendance-row-critical:hover > td {
          background-color: #ffe8e6 !important;
        }
      `}</style>

      {/* Attendance Grid */}
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowClassName={getRowClassName}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (t) => `Tổng: ${t} nhân viên VP`,
        }}
        size="small"
        bordered
        scroll={{ x: 900 }}
      />
    </div>
  );
}
