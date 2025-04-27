import React, { useState, useEffect } from 'react';
import { Container, Typography, TextField, Button, Box } from '@mui/material';
import { fetchUsers, updateUser } from '../api';
import { useParams, useNavigate } from 'react-router-dom';

const EditUser = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [userData, setUserData] = useState({ username: '', email: '' });

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token');
      const res = await fetchUsers(token);
      const user = res.data.find(u => u.id === parseInt(id));
      if (user) {
        setUserData({ username: user.login, email: user.email });
      } else {
        navigate('/users');
      }
    };
    loadUser();
  }, [id, navigate]);

  const handleChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    try {
      await updateUser(id, userData, token);
      navigate('/users');
    } catch (error) {
      console.error('Ошибка обновления пользователя', error);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8 }}>
        <Typography variant="h5" gutterBottom>Редактировать пользователя</Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            margin="normal"
            label="Логин"
            name="username"
            value={userData.username}
            onChange={handleChange}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Email"
            name="email"
            value={userData.email}
            onChange={handleChange}
          />
          <Button fullWidth variant="contained" type="submit" sx={{ mt: 2 }}>
            Сохранить
          </Button>
          <Button fullWidth variant="outlined" sx={{ mt: 2 }} onClick={() => navigate('/users')}>
            Назад
          </Button>
        </form>
      </Box>
    </Container>
  );
};

export default EditUser;
