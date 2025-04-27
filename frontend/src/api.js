// frontend/src/api.js
import axios from 'axios';

// Создаём инстанс axios с базовым URL и JSON по умолчанию
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Интерцептор для автоподстановки JWT в заголовок
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => Promise.reject(error));

// Эндпоинты
export const login = (username, password) =>
  api.post('/users/token', { username, password });

export const fetchUsers = () =>
  api.get('/users/');

export const addUser = (userData) =>
  api.post('/users/add', userData);

export const deleteUser = (userId) =>
  api.delete(`/users/${userId}`);

export const updateUser = (userId, updatedData) =>
  api.put(`/users/${userId}`, updatedData);

export default api;
