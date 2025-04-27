import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Box } from '@mui/material';
import { addUser } from '../api';
import { useNavigate } from 'react-router-dom';

const AddUser = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const navigate = useNavigate();

const handleSubmit = async (e) => {
  e.preventDefault();
  const token = localStorage.getItem('access_token');
  console.log('Отправляем токен:', token);    // ← добавьте это

  try {
    await addUser({ username, email, password, role }, token);
    navigate('/users');
  } catch (error) {
    console.error('Ошибка создания пользователя', error);

    if (error.response && error.response.status === 401) {
      // Если токен неправильный — кидаем на логин
      localStorage.removeItem('access_token');
      navigate('/login');
    }
  }
};

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8 }}>
        <Typography variant="h5" gutterBottom>Добавить пользователя</Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            margin="normal"
            label="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Роль (admin/user)"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          />
          <Button fullWidth variant="contained" type="submit" sx={{ mt: 2 }}>
            Сохранить
          </Button>
        </form>
      </Box>
    </Container>
  );
};

export default AddUser;
