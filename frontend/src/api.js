import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
});

export const login = (username, password) =>
  api.post('/api/users/token', { username, password });

export const fetchUsers = (token) =>
  api.get('/api/users/', { headers: { Authorization: `Bearer ${token}` } });

export default api;
