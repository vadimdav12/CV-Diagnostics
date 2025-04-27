import React, { useEffect, useState } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Stack } from '@mui/material';
import { fetchUsers, deleteUser } from '../api';
import { useNavigate } from 'react-router-dom';

const Users = () => {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  const loadUsers = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const res = await fetchUsers(token);
      setUsers(res.data);
    } catch (error) {
      console.error('Ошибка загрузки пользователей', error);
    }
  };

  const handleDelete = async (userId) => {
    const token = localStorage.getItem('access_token');
    try {
      await deleteUser(userId, token);
      loadUsers(); // перезагрузить после удаления
    } catch (error) {
      console.error('Ошибка удаления пользователя', error);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Пользователи</Typography>
      <Button variant="contained" sx={{ mb: 2 }} onClick={() => navigate('/add-user')}>
        Добавить пользователя
      </Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Логин</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Роль</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.login}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.role.join(', ')}</TableCell>
                <TableCell>
                  <Stack spacing={1} direction="row">
                    <Button variant="outlined" onClick={() => navigate(`/edit-user/${user.id}`)}>
                      Изменить
                    </Button>
                    <Button color="error" onClick={() => handleDelete(user.id)}>
                      Удалить
                    </Button>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Users;
