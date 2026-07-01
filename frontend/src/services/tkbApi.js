import api from './api';

// ─── TKB Data ────────────────────────────────────────────────────────────────

/** Get TKB records for a specific month/year */
export const getTKB = (thang, nam) =>
  api.get(`/tkb/${thang}/${nam}`).then((r) => r.data);

/** Import TKB data (pre-parsed JSON rows) */
export const importTKB = (data, replace = false) =>
  api.post('/tkb/import', { ...data, replace_existing: replace }).then((r) => r.data);

/** Get TKB template info (column definitions) */
export const getTKBTemplate = () =>
  api.get('/tkb/template').then((r) => r.data);

// ─── Change Log (Thay đổi người dạy) ────────────────────────────────────────

/** Get change log records for a specific month/year */
export const getThayDoi = (thang, nam) =>
  api.get(`/tkb/thay-doi/${thang}/${nam}`).then((r) => r.data);

/** Create a single change record */
export const createThayDoi = (data) =>
  api.post('/tkb/thay-doi', data).then((r) => r.data);

/** Update an existing change record */
export const updateThayDoi = (id, data) =>
  api.put(`/tkb/thay-doi/${id}`, data).then((r) => r.data);

/** Delete a change record */
export const deleteThayDoi = (id) =>
  api.delete(`/tkb/thay-doi/${id}`);

/** Bulk import change records */
export const importThayDoi = (rows) =>
  api.post('/tkb/thay-doi/import', rows).then((r) => r.data);

// ─── BCC (Bảng chấm công giảng dạy) ─────────────────────────────────────────

/** Create a manual BCC adjustment (phát sinh) */
export const createPhatSinh = (data) =>
  api.post('/tkb/phat-sinh', data).then((r) => r.data);

/** Get BCC summary report for a specific month/year */
export const getBCCReport = (thang, nam) =>
  api.get(`/bao-cao/bcc/${thang}/${nam}`).then((r) => r.data);
