import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Авто-подставляем JWT
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const login       = (u, p) => api.post('/users/token', { username: u, password: p });

// Users
export const fetchUsers  = ()      => api.get('/users/');
export const addUser     = (d)     => api.post('/users/add', d);
export const updateUser  = (id, d) => api.put(`/users/${id}`, d);
export const deleteUser  = (id)    => api.delete(`/users/${id}`);

// Equipment
export const fetchEquipments   = ()        => api.get('/equipment/');
export const addEquipment      = (data)   => api.post('/equipment/add', data);
export const updateEquipment   = (id, d)   => api.put(`/equipment/${id}`, d);
export const deleteEquipment   = (id)      => api.delete(`/equipment/${id}`);

// Эндпоинты для датчиков на оборудовании
export const addSensorToEquip  = (equipmentId, data) =>
  api.post(`/equipment/${equipmentId}/sensors`, data);

export default api;
