import api from './api';

// --- Nhân viên CRUD ---
export const getNhanVienList = (params) => api.get('/nhan-vien', { params });
export const getNhanVien = (id) => api.get(`/nhan-vien/${id}`);
export const createNhanVien = (data) => api.post('/nhan-vien', data);
export const updateNhanVien = (id, data) => api.put(`/nhan-vien/${id}`, data);
export const deleteNhanVien = (id) => api.delete(`/nhan-vien/${id}`);

// --- Hợp đồng (Contracts) ---
export const getHopDong = (nvId) => api.get(`/nhan-vien/${nvId}/hop-dong`);
export const createHopDong = (nvId, data) => api.post(`/nhan-vien/${nvId}/hop-dong`, data);
export const updateHopDong = (nvId, hdId, data) => api.put(`/nhan-vien/${nvId}/hop-dong/${hdId}`, data);

// --- Nghiệp vụ assignment ---
export const getNghiepVuAssignments = (nvId) => api.get(`/nhan-vien/${nvId}/nghiep-vu`);
export const assignNghiepVu = (nvId, data) => api.post(`/nhan-vien/${nvId}/nghiep-vu`, data);
export const removeNghiepVu = (nvId, id) => api.delete(`/nhan-vien/${nvId}/nghiep-vu/${id}`);

// --- Kiêm nhiệm assignment ---
export const getKiemNhiemAssignments = (nvId) => api.get(`/nhan-vien/${nvId}/kiem-nhiem`);
export const assignKiemNhiem = (nvId, data) => api.post(`/nhan-vien/${nvId}/kiem-nhiem`, data);
export const removeKiemNhiem = (nvId, id) => api.delete(`/nhan-vien/${nvId}/kiem-nhiem/${id}`);

// --- Import employees (JSON body with parsed rows) ---
export const importNhanVien = (data) => api.post('/nhan-vien/import', data);

// --- Lương Khoán breakdown ---
export const getLuongKhoan = (nvId) => api.get(`/luong/luong-khoan/${nvId}`);
