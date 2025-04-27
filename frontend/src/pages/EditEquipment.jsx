import React, { useState, useEffect } from 'react';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { fetchEquipments, updateEquipment } from '../api';
import { useParams, useNavigate } from 'react-router-dom';

export default function EditEquipment() {
  const { id } = useParams();
  const [name, setName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const res = await fetchEquipments();
      const eq = res.data.find(e => e.id === parseInt(id));
      if (eq) setName(eq.name);
      else navigate('/manage-equipment');
    })();
  }, [id, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateEquipment(id, { name });
      navigate('/manage-equipment');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt:4 }}>
      <Typography variant="h5" gutterBottom>Редактировать оборудование</Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Название"
          value={name}
          onChange={e => setName(e.target.value)}
          sx={{ mb:2 }}
        />
        <Button variant="contained" type="submit">Сохранить</Button>
      </Box>
    </Container>
  );
}
