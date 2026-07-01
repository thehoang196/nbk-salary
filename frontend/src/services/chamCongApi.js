import api from './api';

// =============================================================================
// Misa Import
// =============================================================================

/**
 * Upload Misa Excel file and import attendance data.
 * @param {File} file - Misa Excel export file
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} Import results with imported_count, total_rows, errors
 */
export const importMisa = (file, thang, nam) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('thang', thang);
  formData.append('nam', nam);
  return api.post('/cham-cong/import-misa', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// =============================================================================
// Daily Attendance CRUD
// =============================================================================

/**
 * List attendance records for a given month/year.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} List of ChamCongResponse
 */
export const getChamCong = (thang, nam) =>
  api.get(`/cham-cong/${thang}/${nam}`);

/**
 * Create a manual attendance entry.
 * @param {Object} data - { nhan_vien_id, ngay, ky_hieu_cong_id, ghi_chu }
 * @returns {Promise} Created ChamCongResponse
 */
export const createChamCong = (data) =>
  api.post('/cham-cong', data);

/**
 * Update an existing attendance record.
 * @param {number} id - Record ID
 * @param {Object} data - { nhan_vien_id, ngay, ky_hieu_cong_id, ghi_chu }
 * @returns {Promise} Updated ChamCongResponse
 */
export const updateChamCong = (id, data) =>
  api.put(`/cham-cong/${id}`, data);

// =============================================================================
// Attendance Summary (Tổng hợp công)
// =============================================================================

/**
 * Get monthly attendance summary per employee.
 * @param {number} thang - Month (1-12)
 * @param {number} nam - Year
 * @returns {Promise} List of TongHopCongResponse
 */
export const getTongHopCong = (thang, nam) =>
  api.get(`/cham-cong/tong-hop/${thang}/${nam}`);
