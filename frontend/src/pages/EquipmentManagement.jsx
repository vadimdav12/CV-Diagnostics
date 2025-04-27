import React, { useEffect, useState } from 'react';
import {
  Container, Typography, Paper, IconButton, Box, List, ListItem, ListItemText, ListItemSecondaryAction
} from '@mui/material';
import { fetchEquipments, deleteEquipment } from '../api';
import { useNavigate } from 'react-router-dom';
import EditIcon   from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

export default function EquipmentManagement() {
  const [equipments, setEquipments] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadEquipments();
  }, []);

  const loadEquipments = async () => {
    try {
      const res = await fetchEquipments();
      setEquipments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить оборудование?')) return;
    try {
      await deleteEquipment(id);
      loadEquipments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Container sx={{ mt:4 }}>
      <Box sx={{ display:'flex', justifyContent:'space-between', alignItems:'center', mb:2 }}>
        <Typography variant="h5">Список оборудования:</Typography>
        <IconButton color="primary" onClick={() => navigate('/add-equipment')}>
          <EditIcon /> {/* Можно заменить на AddIcon */}
        </IconButton>
      </Box>

      <Paper>
        <List>
          {equipments.map(eq => (
            <ListItem key={eq.id} divider>
              {/* Здесь можно заменить на <ListItemAvatar> с иконкой */}
              <ListItemText
                primary={eq.name}
                secondary="Датчики: тепловые, вибрационные, токовые"
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => navigate(`/edit-equipment/${eq.id}`)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" color="error" onClick={() => handleDelete(eq.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
}
