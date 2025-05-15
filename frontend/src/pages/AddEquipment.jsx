import React, { useState, useEffect } from 'react';
import {
  Container, Typography, TextField, Button, Box,
  IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Paper,
  Select, MenuItem, InputLabel, FormControl, CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function AddEquipment() {
  const [name, setName] = useState('');
  const [sensors, setSensors] = useState([{
    name: '',
    typeId: '',
    dataSource: ''
  }]);
  const [sensorTypes, setSensorTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);
  const navigate = useNavigate();

  // Загрузка типов датчиков при монтировании
  useEffect(() => {
    const fetchSensorTypes = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('/api/sensor-type/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'accept': 'application/json'
          }
        });
        setSensorTypes(response.data);
      } catch (error) {
        console.error('Ошибка загрузки типов датчиков:', error);
      }
    };
    fetchSensorTypes();
  }, []);

  const handleAddSensorField = () => {
    setSensors(prev => [...prev, { name: '', typeId: '', dataSource: '' }]);
  };

  const handleRemoveSensorField = (idx) => {
    setSensors(prev => prev.filter((_, i) => i !== idx));
  };

  const handleSensorChange = (idx, field, value) => {
    setSensors(prev => prev.map((sensor, i) => 
      i === idx ? { ...sensor, [field]: value } : sensor
    ));
  };

  const handleFileChange = (e) => {
    setImage(e.target.files[0] || null);
  };

  const handleCancel = () => {
    navigate(-1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem('access_token');

    try {
      // 1. Добавляем оборудование
      const equipmentResponse = await axios.post('/api/equipment/add', 
        { name }, 
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'accept': 'application/json'
          }
        }
      );
      const equipmentId = equipmentResponse.data.id;

      // 2. Добавляем датчики к оборудованию
      for (const sensor of sensors) {
        if (sensor.name.trim() && sensor.typeId && sensor.dataSource.trim()) {
          await axios.post('/api/sensors/add', 
            {
              name: sensor.name,
              sensor_type_id: sensor.typeId,
              data_source: sensor.dataSource,
              equipment_id: equipmentId
            },
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'accept': 'application/json'
              }
            }
          );
        }
      }

      // 3. (Опционально) Загрузка изображения
      if (image) {
        const formData = new FormData();
        formData.append('image', image);
        // await axios.post(`/api/equipment/${equipmentId}/upload`, formData, {
        //   headers: {
        //     'Authorization': `Bearer ${token}`,
        //     'Content-Type': 'multipart/form-data'
        //   }
        // });
      }

      navigate('/manage-equipment');
    } catch (error) {
      console.error('Ошибка при добавлении оборудования:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>Добавить оборудование</Typography>

        <Box component="form" onSubmit={handleSubmit}>
          {/* Название оборудования */}
          <TextField
            label="Название оборудования"
            value={name}
            onChange={e => setName(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />

          {/* Список датчиков */}
          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Датчики:</Typography>
          <List dense>
            {sensors.map((sensor, idx) => (
              <ListItem key={idx} sx={{ flexDirection: 'column', alignItems: 'flex-start', gap: 2 }}>
                <Box sx={{ width: '100%', display: 'flex', gap: 2 }}>
                  {/* Название датчика */}
                  <TextField
                    label="Название датчика"
                    value={sensor.name}
                    onChange={e => handleSensorChange(idx, 'name', e.target.value)}
                    sx={{ flex: 2 }}
                    required
                  />
                  
                  {/* Тип датчика */}
                  <FormControl sx={{ flex: 1 }}>
                    <InputLabel>Тип</InputLabel>
                    <Select
                      value={sensor.typeId}
                      label="Тип"
                      onChange={e => handleSensorChange(idx, 'typeId', e.target.value)}
                      required
                    >
                      {sensorTypes.map(type => (
                        <MenuItem key={type.id} value={type.id}>
                          {type.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
                
                {/* Источник данных */}
                <TextField
                  label="Источник данных (MQTT)"
                  value={sensor.dataSource}
                  onChange={e => handleSensorChange(idx, 'dataSource', e.target.value)}
                  placeholder="sensor/a1"
                  fullWidth
                  required
                />
                
                <ListItemSecondaryAction sx={{ right: 0, top: 0 }}>
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
          <Box sx={{ mb: 2, mt: 2 }}>
            <Button variant="outlined" component="label">
              Загрузить изображение
              <input type="file" hidden accept="image/*" onChange={handleFileChange} />
            </Button>
            {image && <Typography sx={{ ml: 1, display: 'inline' }}>{image.name}</Typography>}
          </Box>

          {/* Кнопки Сохранить / Отмена */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 2 }}>
            <Button onClick={handleCancel} disabled={loading}>Отмена</Button>
            <Button 
              variant="contained" 
              type="submit"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Сохранение...' : 'Сохранить'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
