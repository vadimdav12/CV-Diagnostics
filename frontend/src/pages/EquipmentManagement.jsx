import React, { useEffect, useState } from 'react';
import {
  Container, Typography, Paper, IconButton, Box, List, ListItem, ListItemText, ListItemSecondaryAction,
  CircularProgress, Alert, Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

export default function EquipmentManagement() {
  const [equipments, setEquipments] = useState([]);
  const [loading, setLoading] = useState({
    list: false,
    delete: false
  });
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Получение заголовка авторизации
  const getAuthHeader = () => ({
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });

  useEffect(() => {
    loadEquipments();
  }, []);

  const loadEquipments = async () => {
    try {
      setLoading(prev => ({ ...prev, list: true }));
      setError(null);
      const res = await axios.get('/api/equipment/', getAuthHeader());
      setEquipments(res.data);
    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError(err.response?.data?.message || 'Ошибка загрузки оборудования');
    } finally {
      setLoading(prev => ({ ...prev, list: false }));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Удалить оборудование ID ${id}?`)) return;
    
    try {
      setLoading(prev => ({ ...prev, delete: true }));
      setError(null);
      
      // Ключевое изменение: простой DELETE запрос с ID в URL
      await axios.delete(`/api/equipment/${id}`, getAuthHeader());
      
      // Оптимистичное обновление UI
      setEquipments(prev => prev.filter(eq => eq.id !== id));
      
    } catch (err) {
      console.error('Ошибка удаления:', err);
      setError(err.response?.data?.message || `Ошибка удаления (${err.response?.status || 'нет ответа'})`);
    } finally {
      setLoading(prev => ({ ...prev, delete: false }));
    }
  };

  if (loading.list && equipments.length === 0) {
    return <CircularProgress sx={{ display: 'block', margin: '2rem auto' }} />;
  }

  return (
    <Container sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Список оборудования</Typography>
        <Button
          startIcon={<EditIcon />}
          onClick={() => navigate('/add-equipment')}
        >
          Добавить
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3}>
        <List>
          {equipments.map(eq => (
            <ListItem key={eq.id} divider>
              <ListItemText
                primary={eq.name}
                secondary={`ID: ${eq.id}`}
              />
              <ListItemSecondaryAction>
                <IconButton 
                  edge="end" 
                  onClick={() => navigate(`/edit-equipment/${eq.id}`)}
                >
                  <EditIcon color="primary" />
                </IconButton>
                <IconButton 
                  edge="end" 
                  onClick={() => handleDelete(eq.id)}
                  disabled={loading.delete}
                >
                  {loading.delete ? <CircularProgress size={24} /> : <DeleteIcon color="error" />}
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
}
