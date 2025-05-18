// frontend/src/pages/Sensors.jsx

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Checkbox,
  TextField,
  MenuItem,
  Select,
  InputLabel,
  FormControl
} from '@mui/material';
import axios from 'axios';

// Преобразование sensor_type_id в человекочитаемое имя
const sensorTypeMap = {
  1: 'токовый',
  2: 'вибрационный',
  3: 'тепловой',
  // Добавь другие при необходимости
};

export default function Sensors() {
  const [equipments, setEquipments] = useState([]);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState('');
  const [sensors, setSensors] = useState([]);
  const [parametersList, setParametersList] = useState([]);
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [assignedParams, setAssignedParams] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }, []);

  useEffect(() => {
    axios.get('/api/equipment').then(r => setEquipments(r.data)).catch(console.error);
    axios.get('/api/parameter').then(r => setParametersList(r.data)).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedEquipmentId) {
      axios
        .get(`/api/equipment/${selectedEquipmentId}/sensors`)
        .then(r => setSensors(r.data.sensors))
        .catch(console.error);
      setSelectedSensor(null);
    }
  }, [selectedEquipmentId]);

  const loadAssigned = sensorId => {
    axios.get(`/api/sensors_parameters/${sensorId}`)
      .then(r => setAssignedParams(r.data))
      .catch(err => {
        if (err.response?.status === 404) setAssignedParams([]);
        else console.error(err);
      });
  };

  const handleSelectSensor = sensor => {
    setSelectedSensor(sensor);
    loadAssigned(sensor.id);
  };

  const toggleAssigned = async (paramId) => {
    if (!selectedSensor) return;
    const sid = selectedSensor.id;
    const isAssigned = assignedParams.some(p => p.parameter_id === paramId);
    try {
      if (isAssigned) {
        await axios.delete(`/api/sensors_parameters/${sid}/${paramId}`);
      } else {
        const key = window.prompt('Введите JSON-ключ для параметра (точечная нотация)', '');
        if (!key) return;
        await axios.post(`/api/sensors_parameters/${sid}/${paramId}`, { key });
      }
      loadAssigned(sid);
    } catch (err) {
      console.error(err);
    }
  };

  const updateKey = async (paramId, newKey) => {
    if (!selectedSensor) return;
    try {
      await axios.put(`/api/sensors_parameters/${selectedSensor.id}/${paramId}`, { key: newKey });
      loadAssigned(selectedSensor.id);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Датчики</Typography>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Выберите оборудование</InputLabel>
        <Select
          value={selectedEquipmentId}
          label="Выберите оборудование"
          onChange={(e) => setSelectedEquipmentId(e.target.value)}
        >
          {equipments.map(eq => (
            <MenuItem key={eq.id} value={eq.id}>{eq.name}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <Grid container spacing={2}>
        {/* Список сенсоров */}
        <Grid item xs={12} md={4}>
          {sensors.length === 0 ? (
            <Typography>Нет датчиков для выбранного оборудования.</Typography>
          ) : (
            sensors.map(s => (
              <Paper
                key={s.id}
                onClick={() => handleSelectSensor(s)}
                sx={{
                  p: 2, mb: 1, cursor: 'pointer',
                  bgcolor: selectedSensor?.id === s.id ? 'action.selected' : 'background.paper'
                }}
              >
                <Typography>
                  {s.name} {sensorTypeMap[s.sensor_type_id] ? `(${sensorTypeMap[s.sensor_type_id]})` : ''}
                </Typography>
              </Paper>
            ))
          )}
        </Grid>

        {/* Параметры */}
        <Grid item xs={12} md={8}>
          {selectedSensor ? (
            <>
              <Typography variant="h6" gutterBottom>
                Параметры для датчика: {selectedSensor.name} {sensorTypeMap[selectedSensor.sensor_type_id] ? `(${sensorTypeMap[selectedSensor.sensor_type_id]})` : ''}
              </Typography>
              {parametersList.map(param => {
                const isAssigned = assignedParams.some(p => p.parameter_id === param.id);
                return (
                  <Box key={param.id} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Checkbox
                      checked={isAssigned}
                      onChange={() => toggleAssigned(param.id)}
                    />
                    <Typography sx={{ mr: 2 }}>{param.name}</Typography>
                    {isAssigned && (
                      <TextField
                        size="small"
                        label="JSON-ключ"
                        value={assignedParams.find(p => p.parameter_id === param.id)?.key || ''}
                        onChange={e => updateKey(param.id, e.target.value)}
                      />
                    )}
                  </Box>
                );
              })}
            </>
          ) : (
            <Typography>Выберите датчик слева, чтобы увидеть и управлять его параметрами.</Typography>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

