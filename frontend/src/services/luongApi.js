import api from './api';

// --- Tính lương (Calculate) ---

/**
 * Calculate salary for all active employees in a given month/year.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @param {number[]|null} nhanVienIds - Optional list of employee IDs to calculate
 * @param {object|null} manualInputs - Optional manual input overrides keyed by nv_id
 */
export const tinhLuongAll = (thang, nam, nhanVienIds = null, manualInputs = null) =>
  api.post('/luong/tinh-luong', {
    thang,
    nam,
    nhan_vien_ids: nhanVienIds,
    manual_inputs: manualInputs,
  });

/**
 * Calculate salary for a single employee.
 * @param {number} nvId - Employee ID
 * @param {number} thang - Month
 * @param {number} nam - Year
 */
export const tinhLuongSingle = (nvId, thang, nam) =>
  api.post(`/luong/tinh-luong/${nvId}`, { thang, nam });

// --- Lương Khoán ---

/**
 * Get Lương Khoán breakdown for an employee.
 * @param {number} nvId - Employee ID
 */
export const getLuongKhoan = (nvId) =>
  api.get(`/luong/luong-khoan/${nvId}`);

// --- Duyệt lương (Approve) ---

/**
 * Approve/advance salary record status (draft → reviewed → approved).
 * Uses optimistic locking via version field.
 * @param {number} id - Salary record ID
 * @param {string} trangThaiMoi - New status ('reviewed' or 'approved')
 * @param {number} version - Current version for conflict detection
 */
export const duyetLuong = (id, trangThaiMoi, version) =>
  api.put(`/luong/duyet/${id}`, { trang_thai_moi: trangThaiMoi, version });

// --- Bảng lương (Salary table) ---

/**
 * Get salary table for a month/year.
 * @param {number} thang - Month
 * @param {number} nam - Year
 */
export const getBangLuong = (thang, nam) =>
  api.get(`/luong/bang-luong/${thang}/${nam}`);

// --- Phiếu lương (Payslip) ---

/**
 * Get individual payslip data.
 * @param {number} nvId - Employee ID
 * @param {number} thang - Month
 * @param {number} nam - Year
 */
export const getPhieuLuong = (nvId, thang, nam) =>
  api.get(`/luong/phieu-luong/${nvId}/${thang}/${nam}`);

// --- Export ---

/**
 * Export payslip as PDF (returns blob).
 * @param {number} nvId - Employee ID
 * @param {number} thang - Month
 * @param {number} nam - Year
 */
export const exportPhieuLuongPdf = (nvId, thang, nam) =>
  api.post(`/export/phieu-luong/${nvId}/${thang}/${nam}`, null, {
    params: { format: 'pdf' },
    responseType: 'blob',
  });

/**
 * Export payslip as Excel (returns blob).
 * @param {number} nvId - Employee ID
 * @param {number} thang - Month
 * @param {number} nam - Year
 */
export const exportPhieuLuongXlsx = (nvId, thang, nam) =>
  api.post(`/export/phieu-luong/${nvId}/${thang}/${nam}`, null, {
    params: { format: 'xlsx' },
    responseType: 'blob',
  });

/**
 * Export salary data in Misa accounting format (returns blob).
 * @param {object} params - Export parameters (thang, nam, etc.)
 */
export const exportMisa = (params = {}) =>
  api.post('/export/misa', params, { responseType: 'blob' });
