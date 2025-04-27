import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Container, Typography, Box } from '@mui/material';
import { login } from '../api';
import { useEffect } from 'react';

const Login = () => {
    useEffect(() => {
    localStorage.removeItem('access_token');
  }, []);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await login(username, password);
      localStorage.setItem('access_token', res.data.access_token);
      navigate('/users');
    } catch (err) {
      setError('Ошибка авторизации. Проверьте логин и пароль.');
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Вход</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <Typography color="error">{error}</Typography>}
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3 }}>
            Войти
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Login;
