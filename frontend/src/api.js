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

// Существующие методы…
export const login       = (u, p) => api.post('/users/token', { username: u, password: p });
export const fetchUsers  = ()      => api.get('/users/');
export const addUser     = (d)     => api.post('/users/add', d);
export const updateUser  = (id, d) => api.put(`/users/${id}`, d);
export const deleteUser  = (id)    => api.delete(`/users/${id}`);

// Новый метод для оборудования
export const fetchEquipments = () =>
  api.get('/equipment/');

export default api;
