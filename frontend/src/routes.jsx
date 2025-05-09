import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login            from './pages/Login';
import EquipmentList    from './pages/EquipmentList';
import Users            from './pages/Users';
import AddUser          from './pages/AddUser';
import EditUser         from './pages/EditUser';
import EquipmentManagement from './pages/EquipmentManagement';
import AddEquipment     from './pages/AddEquipment';
import EditEquipment    from './pages/EditEquipment';
import PrivateRoute     from './components/PrivateRoute';
import MainLayout       from './components/MainLayout';
import Configurator from './pages/Configurator';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Всё защищённое */}
      <Route element={<PrivateRoute><MainLayout/></PrivateRoute>}>
        {/* Доступно всем */}
        <Route path="/" element={<EquipmentList />} />
        <Route path="/configurator" element={<Configurator />} />


        {/* Только admin */}
        <Route path="/users" element={<Users />} />
        <Route path="/add-user" element={<AddUser />} />
        <Route path="/edit-user/:id" element={<EditUser />} />

        <Route path="/manage-equipment" element={<EquipmentManagement />} />
        <Route path="/add-equipment" element={<AddEquipment />} />
        <Route path="/edit-equipment/:id" element={<EditEquipment />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
