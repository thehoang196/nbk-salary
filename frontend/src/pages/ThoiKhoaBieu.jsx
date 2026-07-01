import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table, Button, Space, DatePicker, message, Modal, Tag, Typography, Card, Statistic, Row, Col,
} from 'antd';
import {
  UploadOutlined, FileSearchOutlined,
  HistoryOutlined, BarChartOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import api from '../services/api';
import ImportExcel from '../components/ImportExcel';

const { Title, Text } = Typography;

const LOAI_TIET_LABELS = {
  chinh_khoa: 'Chính khóa',
  tnst_vy: 'TNST VY',
  k9_luyen_thi: 'K9 Luyện thi',
  kh_ta: 'KH bằng TA',
  ielts: 'IELTS',
};

const LOAI_TIET_COLORS = {
  chinh_khoa: 'blue',
  tnst_vy: 'green',
  k9_luyen_thi: 'orange',
  kh_ta: 'purple',
  ielts: 'cyan',
};

export default function ThoiKhoaBieu() {
  const navigate = useNavigate();

  // State
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [importSummary, setImportSummary] = useState(null);

  const thang = selectedMonth.month() + 1;
  const nam = selectedMonth.year();

  // Fetch TKB data for selected month/year
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(`/tkb/${thang}/${nam}`);
      setData(res.data);
    } catch (e) {
      if (e.response?.status !== 404) {
        message.error('Lỗi tải dữ liệu thời khóa biểu');
      }
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [thang, nam]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle month change
  const handleMonthChange = (date) => {
    if (date) {
      setSelectedMonth(date);
      setImportSummary(null);
    }
  };

  // Handle import confirm — parse the school's TKB Excel format
  const handleImportConfirm = async (file) => {
    const XLSX = await import('xlsx');
    const arrayBuffer = await file.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });

    // Parse all sheets - each sheet is a grade (Khối 6, 7, 8, 9)
    const allRows = [];
    const parseErrors = [];

    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName];
      const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

      // Detect which Khối this sheet belongs to
      let khoiName = '';
      const khoiMatch = sheetName.match(/[Kk]h[oố]i\s*(\d+)/i) ||
        rawData.slice(0, 5).flatMap(r => r.join(' ').match(/[Kk]h[oố]i\s*(\d+)/i) || []).filter(Boolean);
      
      // Try to find khoi from sheet name or header rows
      for (let i = 0; i < Math.min(5, rawData.length); i++) {
        const rowText = rawData[i].join(' ');
        const match = rowText.match(/KHỐI\s*(\d+)/i) || rowText.match(/Kh[oố]i\s*(\d+)/i);
        if (match) {
          khoiName = `Khối ${match[1]}`;
          break;
        }
      }
      if (!khoiName) {
        const snMatch = sheetName.match(/(\d+)/);
        if (snMatch) khoiName = `Khối ${snMatch[1]}`;
      }
      if (!khoiName) continue; // Skip sheets we can't identify

      // Find the header row with "LỚP" and class names
      let headerRowIdx = -1;
      let classNames = [];
      let classStartCols = []; // Column indices where each class's Môn column starts

      for (let i = 0; i < Math.min(10, rawData.length); i++) {
        const row = rawData[i];
        const rowStr = row.join('|');
        if (rowStr.includes('LỚP') || rowStr.includes('Lớp')) {
          headerRowIdx = i;
          break;
        }
      }

      if (headerRowIdx === -1) continue;

      // Find the sub-header row with "Thứ", "Tiết", "Môn", "GV"
      let dataHeaderIdx = -1;
      for (let i = headerRowIdx; i < Math.min(headerRowIdx + 3, rawData.length); i++) {
        const row = rawData[i];
        const rowStr = row.join('|').toLowerCase();
        if (rowStr.includes('thứ') && rowStr.includes('tiết') && (rowStr.includes('môn') || rowStr.includes('gv'))) {
          dataHeaderIdx = i;
          break;
        }
      }

      if (dataHeaderIdx === -1) continue;

      // Extract class names from header row
      // Format: LỚP | (empty) | classA | (empty) | classB | (empty) | ...
      // Or: Thứ | Tiết | Môn | GV | Môn | GV | ...
      // Classes appear at every 2 columns starting from col 2 (Môn, GV pairs)
      const lopRow = rawData[headerRowIdx];
      const subHeaderRow = rawData[dataHeaderIdx];
      
      // Find where Môn/GV columns start
      let firstMonCol = -1;
      for (let c = 0; c < subHeaderRow.length; c++) {
        const cell = String(subHeaderRow[c] || '').trim().toLowerCase();
        if (cell === 'môn' || cell === 'mon') {
          firstMonCol = c;
          break;
        }
      }
      if (firstMonCol === -1) firstMonCol = 2; // Default: skip Thứ, Tiết

      // Each class occupies 2 columns (Môn, GV)
      for (let c = firstMonCol; c < subHeaderRow.length; c += 2) {
        // Look for class name in the header row above at same column range
        let className = '';
        // Check lopRow at this column position
        for (let searchRow = headerRowIdx; searchRow <= dataHeaderIdx; searchRow++) {
          const r = rawData[searchRow];
          for (let cc = c; cc <= c + 1 && cc < (r?.length || 0); cc++) {
            const val = String(r[cc] || '').trim();
            if (val && !['Môn', 'GV', 'Thứ', 'Tiết', 'LỚP', 'Lớp', 'môn', 'gv'].includes(val) && val.length < 15) {
              className = val;
            }
          }
        }
        if (className) {
          classNames.push(className);
          classStartCols.push(c);
        }
      }

      if (classNames.length === 0) continue;

      // Parse data rows (after sub-header)
      // Count occurrences: { "GV|Môn|Lớp": count }
      const tietCount = {};
      let currentThu = '';

      for (let i = dataHeaderIdx + 1; i < rawData.length; i++) {
        const row = rawData[i];
        if (!row || row.length === 0) continue;

        // Check if row has "Thứ" value in col 0
        const thuVal = String(row[0] || '').trim();
        if (thuVal && (thuVal.match(/^(Hai|Ba|Tư|Năm|Sáu|Bảy|CN)$/i) || thuVal.match(/^Th[ứu]/i))) {
          currentThu = thuVal;
        }

        // For each class, read Môn and GV
        for (let ci = 0; ci < classNames.length; ci++) {
          const monCol = classStartCols[ci];
          const gvCol = monCol + 1;
          
          const monVal = String(row[monCol] || '').trim();
          const gvVal = String(row[gvCol] || '').trim();

          // Skip empty or special rows (ÂN-NT, AN-NT, etc.)
          if (!monVal || !gvVal) continue;
          if (monVal.match(/^[ÂA]N\s*-?\s*NT$/i)) continue;

          const key = `${gvVal}|||${monVal}|||${classNames[ci]}`;
          tietCount[key] = (tietCount[key] || 0) + 1;
        }
      }

      // Convert counts to rows
      for (const [key, count] of Object.entries(tietCount)) {
        const [gv, mon, lop] = key.split('|||');
        allRows.push({
          giao_vien: gv,
          mon_hoc: mon,
          khoi: khoiName,
          lop: lop,
          so_tiet: count,
          loai_tiet: 'chinh_khoa',
        });
      }
    }

    if (allRows.length === 0) {
      return {
        imported_count: 0,
        total_rows: 0,
        errors: [{ row: 0, message: 'Không đọc được dữ liệu từ file. Kiểm tra lại định dạng file.' }],
      };
    }

    // Send parsed rows to backend
    try {
      const res = await api.post('/tkb/import', {
        thang,
        nam,
        rows: allRows,
        replace_existing: false,
      });
      const result = res.data;
      setImportSummary(result);
      fetchData();
      return result;
    } catch (e) {
      if (e.response?.status === 409) {
        // Month already has data — ask user to confirm replace
        return new Promise((resolve, reject) => {
          Modal.confirm({
            title: 'Dữ liệu đã tồn tại',
            content: (
              <div>
                <p>Dữ liệu TKB tháng {thang}/{nam} đã tồn tại trong hệ thống.</p>
                <p>Bạn có muốn <strong>ghi đè</strong> dữ liệu cũ không?</p>
              </div>
            ),
            okText: 'Ghi đè',
            okType: 'danger',
            cancelText: 'Hủy',
            onOk: async () => {
              try {
                const res2 = await api.post('/tkb/import', {
                  thang,
                  nam,
                  rows: allRows,
                  replace_existing: true,
                });
                const result2 = res2.data;
                setImportSummary(result2);
                fetchData();
                resolve(result2);
              } catch (err) {
                reject(err);
              }
            },
            onCancel: () => {
              reject({ cancelled: true });
            },
          });
        });
      }
      throw e;
    }
  };

  // Template download URL is no longer needed - import uses actual school TKB format
  const templateUrl = null;

  // Table columns
  const columns = [
    {
      title: 'STT',
      key: 'stt',
      width: 60,
      align: 'center',
      render: (_, __, idx) => idx + 1,
    },
    {
      title: 'Giáo viên',
      dataIndex: 'nhan_vien_ho_ten',
      key: 'nhan_vien_ho_ten',
      width: 180,
      render: (val, record) => val || `NV #${record.nhan_vien_id}`,
    },
    {
      title: 'Môn học',
      dataIndex: 'mon_hoc_ten',
      key: 'mon_hoc_ten',
      width: 150,
      render: (val, record) => val || `MH #${record.mon_hoc_id}`,
    },
    {
      title: 'Khối',
      dataIndex: 'khoi_ten',
      key: 'khoi_ten',
      width: 100,
      render: (val, record) => val || `K #${record.khoi_id}`,
    },
    {
      title: 'Lớp',
      dataIndex: 'lop_ten',
      key: 'lop_ten',
      width: 100,
      render: (val, record) => val || `L #${record.lop_id}`,
    },
    {
      title: 'Số tiết',
      dataIndex: 'so_tiet',
      key: 'so_tiet',
      width: 90,
      align: 'center',
    },
    {
      title: 'Loại tiết',
      dataIndex: 'loai_tiet',
      key: 'loai_tiet',
      width: 130,
      render: (val) => (
        <Tag color={LOAI_TIET_COLORS[val] || 'default'}>
          {LOAI_TIET_LABELS[val] || val}
        </Tag>
      ),
    },
  ];

  // Calculate summary statistics
  const totalRecords = data.length;
  const totalPeriods = data.reduce((sum, r) => sum + (r.so_tiet || 0), 0);
  const uniqueTeachers = new Set(data.map((r) => r.nhan_vien_id)).size;

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Thời khóa biểu</Title>
        <Space>
          <Button
            icon={<BarChartOutlined />}
            onClick={() => navigate('/bcc')}
          >
            BCC Tổng tiết
          </Button>
          <Button
            icon={<HistoryOutlined />}
            onClick={() => navigate('/tkb/thay-doi')}
          >
            Nhật ký thay đổi
          </Button>
        </Space>
      </div>

      {/* Month selector + Import button */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Text strong>Tháng/Năm:</Text>
            <DatePicker
              picker="month"
              value={selectedMonth}
              onChange={handleMonthChange}
              format="MM/YYYY"
              allowClear={false}
              style={{ width: 150 }}
            />
          </Space>
        </Col>
        <Col flex="auto" style={{ textAlign: 'right' }}>
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setImportOpen(true)}
            >
              Import TKB
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Summary statistics */}
      {data.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Tổng bản ghi" value={totalRecords} />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Tổng số tiết" value={totalPeriods} />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic title="Số giáo viên" value={uniqueTeachers} />
            </Card>
          </Col>
        </Row>
      )}

      {/* Import summary after successful import */}
      {importSummary && (
        <Card
          size="small"
          style={{ marginBottom: 16, borderColor: '#52c41a' }}
          title={
            <Space>
              <FileSearchOutlined style={{ color: '#52c41a' }} />
              <Text strong>Kết quả import</Text>
            </Space>
          }
        >
          <Row gutter={16}>
            <Col span={8}>
              <Statistic
                title="Đã import"
                value={importSummary.imported_count}
                suffix="dòng"
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Tổng dòng"
                value={importSummary.total_rows}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Lỗi"
                value={importSummary.errors?.length || 0}
                valueStyle={importSummary.errors?.length > 0 ? { color: '#cf1322' } : undefined}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* Data table */}
      <Table
        dataSource={data}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        scroll={{ x: 900 }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100'],
          showTotal: (total) => `Tổng ${total} bản ghi`,
        }}
        locale={{ emptyText: `Không có dữ liệu TKB tháng ${thang}/${nam}` }}
      />

      {/* Import modal */}
      <ImportExcel
        title={`Import TKB tháng ${thang}/${nam}`}
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onConfirm={handleImportConfirm}
        accept=".xlsx,.xls,.csv"
        maxSize={10}
        templateUrl={templateUrl}
      />
    </div>
  );
}
