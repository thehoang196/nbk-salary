import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, DatePicker, InputNumber, Popover, Input, Button, Tag,
  Tooltip, message, Space, Typography,
} from 'antd';
import { ReloadOutlined, EditOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';

const { Title } = Typography;

/**
 * Round a number to 1 decimal place
 */
const round1 = (val) => {
  if (val == null) return null;
  return Math.round(val * 10) / 10;
};

/**
 * Format a period value to 1 decimal place display
 */
const formatTiet = (val) => {
  if (val == null) return '—';
  return round1(val).toFixed(1);
};

export default function BCCTongTiet() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(dayjs());

  // Inline editing state
  const [editingKey, setEditingKey] = useState(null);
  const [editValue, setEditValue] = useState(null);
  const [editReason, setEditReason] = useState('');
  const [savingKey, setSavingKey] = useState(null);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  const fetchBCC = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/bao-cao/bcc/${thang}/${nam}`);
      setData(res.data);
    } catch (e) {
      message.error('Lỗi tải dữ liệu BCC');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  useEffect(() => {
    fetchBCC();
  }, [fetchBCC]);

  const handleMonthChange = (date) => {
    if (date) {
      setSelectedMonth(date);
      setEditingKey(null);
    }
  };

  const startEdit = (record) => {
    setEditingKey(record.nhan_vien_id);
    setEditValue(record.phat_sinh || 0);
    setEditReason('');
  };

  const cancelEdit = () => {
    setEditingKey(null);
    setEditValue(null);
    setEditReason('');
  };

  const saveEdit = async (record) => {
    if (!editReason || editReason.trim().length === 0) {
      message.warning('Vui lòng nhập lý do điều chỉnh');
      return;
    }
    if (editReason.trim().length > 200) {
      message.warning('Lý do tối đa 200 ký tự');
      return;
    }

    setSavingKey(record.nhan_vien_id);
    try {
      await api.post('/tkb/phat-sinh', {
        nhan_vien_id: record.nhan_vien_id,
        so_tiet: editValue,
        ly_do: editReason.trim(),
      });
      message.success('Đã lưu điều chỉnh phát sinh');
      setEditingKey(null);
      setEditValue(null);
      setEditReason('');
      fetchBCC();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Lỗi lưu điều chỉnh');
    } finally {
      setSavingKey(null);
    }
  };

  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 50,
      fixed: 'left',
      align: 'center',
      render: (_, __, index) => index + 1,
    },
    {
      title: 'Giáo viên',
      key: 'giao_vien',
      width: 160,
      fixed: 'left',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.ho_ten}</div>
          {record.ten_goi && (
            <div style={{ fontSize: 12, color: '#666' }}>({record.ten_goi})</div>
          )}
        </div>
      ),
    },
    {
      title: 'Theo TKB',
      dataIndex: 'theo_tkb',
      key: 'theo_tkb',
      width: 90,
      align: 'right',
      render: (val) => formatTiet(val),
    },
    {
      title: 'Thay đổi',
      dataIndex: 'thay_doi',
      key: 'thay_doi',
      width: 90,
      align: 'right',
      render: (val) => {
        if (val == null) return '—';
        const rounded = round1(val);
        const color = rounded > 0 ? '#52c41a' : rounded < 0 ? '#ff4d4f' : undefined;
        return (
          <span style={{ color }}>
            {rounded > 0 ? '+' : ''}{rounded.toFixed(1)}
          </span>
        );
      },
    },
    {
      title: 'Phát sinh',
      key: 'phat_sinh',
      width: 160,
      align: 'center',
      render: (_, record) => {
        const isEditing = editingKey === record.nhan_vien_id;
        const isSaving = savingKey === record.nhan_vien_id;

        if (isEditing) {
          return (
            <Popover
              open={true}
              placement="bottom"
              title="Lý do điều chỉnh"
              content={
                <div style={{ width: 250 }}>
                  <Input.TextArea
                    rows={2}
                    maxLength={200}
                    value={editReason}
                    onChange={(e) => setEditReason(e.target.value)}
                    placeholder="Nhập lý do (bắt buộc, tối đa 200 ký tự)"
                    showCount
                  />
                  <div style={{ marginTop: 8, textAlign: 'right' }}>
                    <Space>
                      <Button size="small" onClick={cancelEdit} icon={<CloseOutlined />}>
                        Hủy
                      </Button>
                      <Button
                        size="small"
                        type="primary"
                        onClick={() => saveEdit(record)}
                        loading={isSaving}
                        icon={<CheckOutlined />}
                      >
                        Lưu
                      </Button>
                    </Space>
                  </div>
                </div>
              }
            >
              <InputNumber
                size="small"
                min={-50}
                max={50}
                step={0.5}
                value={editValue}
                onChange={(val) => setEditValue(val)}
                style={{ width: 80 }}
                precision={1}
              />
            </Popover>
          );
        }

        const val = record.phat_sinh;
        return (
          <Space size="small">
            <span>{val != null ? formatTiet(val) : '0.0'}</span>
            <Tooltip title="Điều chỉnh phát sinh">
              <Button
                size="small"
                type="text"
                icon={<EditOutlined />}
                onClick={() => startEdit(record)}
              />
            </Tooltip>
          </Space>
        );
      },
    },
    {
      title: 'Thực tế',
      children: [
        {
          title: 'Tiết chính',
          dataIndex: ['thuc_te', 'tiet_chinh_hs1'],
          key: 'tiet_chinh',
          width: 90,
          align: 'right',
          render: (val) => formatTiet(val),
        },
        {
          title: (
            <Tooltip title="Trường ngoại sở tại Vĩnh Yên (HS 1.3)">
              TNST VY
            </Tooltip>
          ),
          dataIndex: ['thuc_te', 'tnst_vy'],
          key: 'tnst_vy',
          width: 85,
          align: 'right',
          render: (val) => formatTiet(val),
        },
        {
          title: (
            <Tooltip title="Khối 9 luyện thi (HS 1.5)">
              K9 LT
            </Tooltip>
          ),
          dataIndex: ['thuc_te', 'k9_lt'],
          key: 'k9_lt',
          width: 80,
          align: 'right',
          render: (val) => formatTiet(val),
        },
        {
          title: (
            <Tooltip title="Khoa học bằng Tiếng Anh">
              KH TA
            </Tooltip>
          ),
          dataIndex: ['thuc_te', 'kh_ta'],
          key: 'kh_ta',
          width: 80,
          align: 'right',
          render: (val) => formatTiet(val),
        },
        {
          title: 'Ielts',
          dataIndex: ['thuc_te', 'ielts'],
          key: 'ielts',
          width: 75,
          align: 'right',
          render: (val) => formatTiet(val),
        },
        {
          title: 'Tổng',
          dataIndex: ['thuc_te', 'tong'],
          key: 'tong',
          width: 85,
          align: 'right',
          render: (val) => (
            <strong>{formatTiet(val)}</strong>
          ),
        },
      ],
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          BCC Tổng tiết
        </Title>
        <Space>
          <DatePicker
            picker="month"
            value={selectedMonth}
            onChange={handleMonthChange}
            format="MM/YYYY"
            allowClear={false}
            style={{ width: 140 }}
          />
          <Tooltip title="Tải lại dữ liệu">
            <Button icon={<ReloadOutlined />} onClick={fetchBCC} loading={loading} />
          </Tooltip>
        </Space>
      </div>

      <div style={{ marginBottom: 12 }}>
        <Space>
          <Tag color="gold">■</Tag>
          <span style={{ fontSize: 12, color: '#666' }}>
            Dòng màu vàng: dữ liệu chưa đầy đủ (thiếu thay đổi hoặc phát sinh)
          </span>
        </Space>
      </div>

      <Table
        dataSource={data}
        columns={columns}
        rowKey="nhan_vien_id"
        loading={loading}
        size="small"
        bordered
        scroll={{ x: 1200 }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100'],
          showTotal: (total) => `Tổng ${total} giáo viên`,
        }}
        rowClassName={(record) =>
          record.is_incomplete ? 'bcc-row-incomplete' : ''
        }
      />

      <style>{`
        .bcc-row-incomplete {
          background-color: #fffbe6 !important;
        }
        .bcc-row-incomplete:hover > td {
          background-color: #fff8cc !important;
        }
        .bcc-row-incomplete > td {
          background-color: #fffbe6 !important;
        }
      `}</style>
    </div>
  );
}
