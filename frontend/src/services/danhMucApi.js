import api from './api';

// Generic catalog CRUD
export const getDanhMuc = (loai) => api.get(`/danh-muc/${loai}`);
export const createDanhMuc = (loai, data) => api.post(`/danh-muc/${loai}`, data);
export const updateDanhMuc = (loai, id, data) => api.put(`/danh-muc/${loai}/${id}`, data);
export const deleteDanhMuc = (loai, id) => api.delete(`/danh-muc/${loai}/${id}`);

// Chức vụ, Cấp bậc, Nghiệp vụ, Kiêm nhiệm
export const getChucVu = () => api.get('/chuc-danh/chuc-vu');
export const createChucVu = (data) => api.post('/chuc-danh/chuc-vu', data);
export const updateChucVu = (id, data) => api.put(`/chuc-danh/chuc-vu/${id}`, data);
export const deleteChucVu = (id) => api.delete(`/chuc-danh/chuc-vu/${id}`);

export const getCapBacQL = () => api.get('/chuc-danh/cap-bac-ql');
export const createCapBacQL = (data) => api.post('/chuc-danh/cap-bac-ql', data);
export const updateCapBacQL = (id, data) => api.put(`/chuc-danh/cap-bac-ql/${id}`, data);
export const deleteCapBacQL = (id) => api.delete(`/chuc-danh/cap-bac-ql/${id}`);

export const getNghiepVu = () => api.get('/chuc-danh/nghiep-vu');
export const createNghiepVu = (data) => api.post('/chuc-danh/nghiep-vu', data);
export const updateNghiepVu = (id, data) => api.put(`/chuc-danh/nghiep-vu/${id}`, data);
export const deleteNghiepVu = (id) => api.delete(`/chuc-danh/nghiep-vu/${id}`);

export const getKiemNhiem = () => api.get('/chuc-danh/kiem-nhiem');
export const createKiemNhiem = (data) => api.post('/chuc-danh/kiem-nhiem', data);
export const updateKiemNhiem = (id, data) => api.put(`/chuc-danh/kiem-nhiem/${id}`, data);
export const deleteKiemNhiem = (id) => api.delete(`/chuc-danh/kiem-nhiem/${id}`);

// Đơn giá dạy
export const getDonGiaDay = (params) => api.get('/don-gia-day', { params });
export const createDonGiaDay = (data) => api.post('/don-gia-day', data);
export const updateDonGiaDay = (id, data) => api.put(`/don-gia-day/${id}`, data);
export const deleteDonGiaDay = (id) => api.delete(`/don-gia-day/${id}`);
