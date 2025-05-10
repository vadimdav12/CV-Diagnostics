// src/pages/Sensors.jsx

import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  FormControlLabel,
  Checkbox,
  Button
} from '@mui/material';
import axios from 'axios';
import { useLocation } from 'react-router-dom';

export default function Sensors() {
  const [sensors, setSensors] = useState([]);
  const [parametersList, setParametersList] = useState([]);
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [assignedParams, setAssignedParams] = useState([]);

  const location = useLocation();
  const equipmentId = location.state?.equipmentId;

  // проставляем токен
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }, []);

  // загрузка сенсоров и справочника параметров
  useEffect(() => {
    const url = equipmentId
      ? `/api/equipment/${equipmentId}/sensors`
      : '/api/sensors';
    axios.get(url).then(r => setSensors(r.data)).catch(console.error);
    axios.get('/api/parameter').then(r => setParametersList(r.data)).catch(console.error);
  }, [equipmentId]);

  // загрузить, что сейчас назначено этому сенсору
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

  // переключить (удалить или добавить) связь sensor–parameter
  const toggleAssigned = async (paramId) => {
    if (!selectedSensor) return;
    const sid = selectedSensor.id;
    const isAssigned = assignedParams.some(p => p.parameter_id === paramId);
    try {
      if (isAssigned) {
        await axios.delete(`/api/sensors_parameters/${sid}/${paramId}`);
      } else {
        await axios.post(`/api/sensors_parameters/${sid}/${paramId}`, { key: '' });
      }
      loadAssigned(sid);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Датчики
      </Typography>
      <Grid container spacing={2}>
        {/* список сенсоров */}
        <Grid item xs={12} md={4}>
          {sensors.map(s => (
            <Paper
              key={s.id}
              onClick={() => handleSelectSensor(s)}
              sx={{
                p: 2, mb: 1, cursor: 'pointer',
                bgcolor: selectedSensor?.id === s.id ? 'grey.200' : 'white'
              }}
            >
              <Typography>
                {s.name} ({s.sensor_type_id})
              </Typography>
            </Paper>
          ))}
        </Grid>

        {/* параметры выбранного сенсора */}
        <Grid item xs={12} md={8}>
          {selectedSensor ? (
            <>
              <Typography variant="h6" gutterBottom>
                Параметры для {selectedSensor.name}
              </Typography>

              {assignedParams.length === 0 && (
                <Typography color="text.secondary">
                  У этого датчика нет назначенных параметров.
                </Typography>
              )}

              {assignedParams.map(ap => {
                const meta = parametersList.find(p => p.id === ap.parameter_id);
                return meta ? (
                  <FormControlLabel
                    key={meta.id}
                    control={
                      <Checkbox
                        checked={true}
                        onChange={() => toggleAssigned(meta.id)}
                      />
                    }
                    label={meta.name}
                  />
                ) : null;
              })}

              <Box sx={{ mt: 2 }}>
                <Button variant="outlined" onClick={() => loadAssigned(selectedSensor.id)}>
                  Обновить
                </Button>
              </Box>
            </>
          ) : (
            <Typography>
              Выберите сенсор слева, чтобы увидеть и управлять его параметрами.
            </Typography>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}
