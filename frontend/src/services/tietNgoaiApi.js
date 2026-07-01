import api from './api';

// List external periods for a given month/year
export const getTietNgoai = (thang, nam) => api.get(`/tiet-ngoai/${thang}/${nam}`);

// Create a single external period entry
export const createTietNgoai = (data) => api.post('/tiet-ngoai', data);

// Update an external period entry
export const updateTietNgoai = (id, data) => api.put(`/tiet-ngoai/${id}`, data);

// Delete an external period entry
export const deleteTietNgoai = (id) => api.delete(`/tiet-ngoai/${id}`);

// Bulk import external periods from Excel file
export const importTietNgoai = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/tiet-ngoai/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
