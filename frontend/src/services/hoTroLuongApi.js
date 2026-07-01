import api from './api';

// List support allowances for a given month/year
export const getHoTroLuong = (thang, nam) => api.get(`/ho-tro-luong/${thang}/${nam}`);

// Create a single support allowance entry
export const createHoTroLuong = (data) => api.post('/ho-tro-luong', data);

// Batch create support allowances (one type for multiple employees)
export const batchCreateHoTroLuong = (data) => api.post('/ho-tro-luong/batch', data);

// Bulk import support allowances from Excel file
export const importHoTroLuong = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/ho-tro-luong/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Update a support allowance entry
export const updateHoTroLuong = (id, data) => api.put(`/ho-tro-luong/${id}`, data);

// Delete a support allowance entry
export const deleteHoTroLuong = (id) => api.delete(`/ho-tro-luong/${id}`);
