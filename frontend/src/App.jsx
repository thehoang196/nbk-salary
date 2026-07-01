import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import useAuthStore from './store/authStore';

import DanhMuc from './pages/DanhMuc';
import MonHoc from './pages/DanhMuc/MonHoc';
import HeSoLuong from './pages/DanhMuc/HeSoLuong';

import NhanVien from './pages/NhanVien';
import NhanVienDetail from './pages/NhanVienDetail';

import BCCTongTiet from './pages/BCCTongTiet';
import ThoiKhoaBieu from './pages/ThoiKhoaBieu';

import TietDayNgoai from './pages/TietDayNgoai';
import HoTroLuong from './pages/HoTroLuong';

import ChamCong from './pages/ChamCong';
import BangLuong from './pages/BangLuong';
import PhieuLuong from './pages/PhieuLuong';
import BaoCao from './pages/BaoCao';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import MisaImport from './pages/MisaImport';

function App() {
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => { if (isAuthenticated) fetchUser(); }, [isAuthenticated, fetchUser]);

  return (
    <ConfigProvider locale={viVN}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="danh-muc" element={<DanhMuc />} />
            <Route path="danh-muc/mon-hoc" element={<MonHoc />} />
            <Route path="danh-muc/he-so-luong" element={<HeSoLuong />} />
            <Route path="nhan-vien" element={<NhanVien />} />
            <Route path="nhan-vien/:id" element={<NhanVienDetail />} />
            <Route path="tkb" element={<ThoiKhoaBieu />} />
            <Route path="bcc" element={<BCCTongTiet />} />
            <Route path="tiet-ngoai" element={<TietDayNgoai />} />
            <Route path="ho-tro-luong" element={<HoTroLuong />} />
            <Route path="cham-cong" element={<ChamCong />} />
            <Route path="bang-luong" element={<BangLuong />} />
            <Route path="phieu-luong/:nvId/:thang/:nam" element={<PhieuLuong />} />
            <Route path="bao-cao" element={<BaoCao />} />
            <Route path="misa-import" element={<MisaImport />} />
            <Route path="quan-ly-user" element={<UserManagement />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
