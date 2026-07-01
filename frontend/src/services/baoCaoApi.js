import api from './api';

// --- BCC Tổng Tiết (Teacher Period Summary) ---

/**
 * Get BCC (teacher period summary) report data.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} JSON response with BCC rows
 */
export const getBCCTongTiet = (thang, nam) =>
  api.get(`/bao-cao/bcc/${thang}/${nam}`);

// --- Tổng Hợp Lương Tháng (Monthly Salary Summary) ---

/**
 * Export monthly salary summary report as Excel file.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} Blob response for file download
 */
export const exportTongHopLuongThang = (thang, nam) =>
  api.get(`/bao-cao/tong-hop/${thang}/${nam}`, { responseType: 'blob' });

// --- Tổng Hợp Lương Năm (Yearly Salary Summary) ---

/**
 * Export yearly salary summary report as Excel file.
 * Aggregates monthly summaries from January to December.
 * @param {number} nam - Year
 * @returns {Promise} Blob response for file download
 */
export const exportTongHopLuongNam = (nam) =>
  api.get(`/bao-cao/tong-hop-nam/${nam}`, { responseType: 'blob' });

// --- Chấm Công (Attendance Report) ---

/**
 * Get monthly attendance summary report data.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} JSON response with attendance records
 */
export const getChamCongReport = (thang, nam) =>
  api.get(`/bao-cao/cham-cong/${thang}/${nam}`);

// --- Export Misa ---

/**
 * Export salary data in Misa-compatible Excel format.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} Blob response for file download
 */
export const exportMisa = (thang, nam) =>
  api.get(`/bao-cao/export-misa/${thang}/${nam}`, { responseType: 'blob' });

// --- Phiếu Lương PDF (Payslip Download) ---

/**
 * Download individual payslip as PDF/HTML.
 * @param {number} nvId - Employee ID
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} Blob response for file download
 */
export const downloadPhieuLuongPdf = (nvId, thang, nam) =>
  api.get(`/bao-cao/phieu-luong-pdf/${nvId}/${thang}/${nam}`, { responseType: 'blob' });

// --- Download Report Excel ---

/**
 * Generic helper to download a report Excel file by triggering the
 * appropriate endpoint based on report type.
 * @param {'tong-hop'|'bcc'|'cham-cong'|'misa'} loaiBaoCao - Report type
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} Blob response for file download
 */
export const downloadReportExcel = (loaiBaoCao, thang, nam) => {
  const endpoints = {
    'tong-hop': `/bao-cao/tong-hop/${thang}/${nam}`,
    'misa': `/bao-cao/export-misa/${thang}/${nam}`,
  };
  const url = endpoints[loaiBaoCao];
  if (!url) {
    return Promise.reject(new Error(`Unknown report type: ${loaiBaoCao}`));
  }
  return api.get(url, { responseType: 'blob' });
};
