import { create } from 'zustand';
import api from '../services/api';

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,

  login: async (username, password) => {
    set({ loading: true });
    try {
      const res = await api.post('/auth/login', { username, password });
      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      set({ token, isAuthenticated: true, loading: false });
      // Fetch user info
      const userRes = await api.get('/auth/me');
      set({ user: userRes.data });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null, isAuthenticated: false });
    window.location.href = '/login';
  },

  fetchUser: async () => {
    try {
      const res = await api.get('/auth/me');
      set({ user: res.data, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
    }
  },
}));

export default useAuthStore;
