import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Users from './pages/Users';
import AddUser from './pages/AddUser';
import PrivateRoute from './components/PrivateRoute';
import EditUser from './pages/EditUser';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Страница логина */}
      <Route path="/login" element={<Login />} />

      {/* Защищённая страница пользователей */}
      <Route
        path="/users"
        element={
          <PrivateRoute>
            <Users />
          </PrivateRoute>
        }
      />

      {/* Защищённая страница добавления пользователя */}
      <Route
        path="/add-user"
        element={
          <PrivateRoute>
            <AddUser />
          </PrivateRoute>
        }
      />
      <Route path="/edit-user/:id" element={<PrivateRoute><EditUser /></PrivateRoute>} />


      {/* Перехват всех остальных маршрутов → редирект на /login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRoutes;
