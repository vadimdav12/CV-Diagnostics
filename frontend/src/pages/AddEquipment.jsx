import React, { useState } from 'react';
import {
  Container, Typography, TextField, Button, Box,
  IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Paper
} from '@mui/material';
import AddIcon    from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { addEquipment, addSensorToEquip } from '../api';
import { useNavigate } from 'react-router-dom';

export default function AddEquipment() {
  const [name, setName] = useState('');
  const [sensors, setSensors] = useState(['']);   // начнём с одного пустого поля
  const [image, setImage] = useState(null);       // хранит файл
  const navigate = useNavigate();

  const handleAddSensorField = () => {
    setSensors(prev => [...prev, '']);
  };

  const handleRemoveSensorField = (idx) => {
    setSensors(prev => prev.filter((_, i) => i !== idx));
  };

  const handleSensorChange = (idx, value) => {
    setSensors(prev => prev.map((v,i) => i===idx ? value : v));
  };

  const handleFileChange = (e) => {
    setImage(e.target.files[0] || null);
  };

  const handleCancel = () => {
    navigate(-1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 1) Добавляем оборудование (без датчиков и картинки)
    const eqRes = await addEquipment({ name });
    const equipmentId = eqRes.data.id;

    // 2) Загружаем датчики
    for (const sensorName of sensors.filter(s=>s.trim())) {
      await addSensorToEquip(equipmentId, {
        name: sensorName,
        // тут туда, куда API ожидает: data_source, sensor_type_id и т.п.
        data_source: sensorName,          // временно
        sensor_type_id: 1,                // временно
      });
    }

    // 3) (опционально) загрузить картинку
    if (image) {
      const fd = new FormData();
      fd.append('image', image);
      // await api.post(`/equipment/${equipmentId}/upload`, fd);
    }

    // 4) Вернуться на список оборудования
    navigate('/manage-equipment');
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>Добавить оборудование</Typography>

        <Box component="form" onSubmit={handleSubmit}>
          {/* Название */}
          <TextField
            label="Название"
            value={name}
            onChange={e => setName(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />

          {/* Список датчиков */}
          <Typography variant="subtitle1">Список датчиков:</Typography>
          <List dense>
            {sensors.map((sensor, idx) => (
              <ListItem key={idx}>
                <ListItemText>
                  <TextField
                    placeholder={`Датчик №${idx+1}`}
                    value={sensor}
                    onChange={e => handleSensorChange(idx, e.target.value)}
                    fullWidth
                  />
                </ListItemText>
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={() => handleRemoveSensorField(idx)}>
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
            <ListItem>
              <Button startIcon={<AddIcon />} onClick={handleAddSensorField}>
                Добавить датчик
              </Button>
            </ListItem>
          </List>

          {/* Загрузка изображения */}
          <Box sx={{ mb: 2 }}>
            <Button variant="outlined" component="label">
              Загрузить изображение
              <input type="file" hidden accept="image/*" onChange={handleFileChange} />
            </Button>
            {image && <Typography sx={{ ml: 1, display: 'inline' }}>{image.name}</Typography>}
          </Box>

          {/* Кнопки Сохранить / Отмена */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={handleCancel}>Отмена</Button>
            <Button variant="contained" type="submit">Сохранить</Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
