import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login         from './pages/Login';
import EquipmentList from './pages/EquipmentList';
import Users         from './pages/Users';
import AddUser       from './pages/AddUser';
import EditUser      from './pages/EditUser';
import PrivateRoute  from './components/PrivateRoute';
import MainLayout    from './components/MainLayout';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Страница логина */}
      <Route path="/login" element={<Login />} />

      {/* Всё, что ниже — только после авторизации */}
      <Route element={<PrivateRoute><MainLayout /></PrivateRoute>}>
        {/* Главная — список оборудования */}
        <Route path="/" element={<EquipmentList />} />

        {/* Управление пользователями */}
        <Route path="/users"      element={<Users />} />
        <Route path="/add-user"   element={<AddUser />} />
        <Route path="/edit-user/:id" element={<EditUser />} />
      </Route>

      {/* Любой нераспознанный маршрут → логин */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
