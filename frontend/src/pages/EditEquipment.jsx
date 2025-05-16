import React, { useState, useEffect } from 'react';
import {
  Container, TextField, Button, Typography, Box,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  IconButton, Select, MenuItem, InputLabel, FormControl, Dialog, DialogActions,
  DialogContent, DialogTitle, CircularProgress, Alert
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CloseIcon from '@mui/icons-material/Close';
import SaveIcon from '@mui/icons-material/Save';
import axios from 'axios';

export default function EditEquipment() {
  const { id } = useParams();
  const [name, setName] = useState('');
  const [sensors, setSensors] = useState([]);
  const [sensorTypes, setSensorTypes] = useState([]);
  const [newSensor, setNewSensor] = useState({
    name: '',
    typeId: '',
    dataSource: ''
  });
  const [editingSensor, setEditingSensor] = useState(null);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [loading, setLoading] = useState({
    page: true,
    equipment: false,
    sensors: false
  });
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const getAuthHeader = () => ({
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json'
    }
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(prev => ({ ...prev, page: true }));
        setError(null);

        // 1. Загружаем список всего оборудования
        const equipmentsRes = await axios.get('/api/equipment/', getAuthHeader());
        
        // 2. Находим нужное оборудование
        const equipment = equipmentsRes.data.find(e => e.id === parseInt(id));
        if (!equipment) {
          throw new Error('Оборудование не найдено');
        }
        setName(equipment.name);

        // 3. Загружаем датчики оборудования
        const sensorsRes = await axios.get(`/api/equipment/${id}/sensors`, getAuthHeader());
        console.log('Получены датчики:', sensorsRes.data); // Для отладки
        
        // Исправление: извлекаем массив из поля sensors
        const sensorsData = sensorsRes.data?.sensors || [];
        setSensors(sensorsData);

        // 4. Загружаем типы датчиков
        const typesRes = await axios.get('/api/sensor-type/', getAuthHeader());
        setSensorTypes(typesRes.data || []);

      } catch (err) {
        console.error('Ошибка загрузки:', err);
        setError(err.response?.data?.message || err.message || 'Ошибка загрузки данных');
        
        if (err.response?.status === 401) {
          localStorage.removeItem('access_token');
          navigate('/login');
        }
      } finally {
        setLoading(prev => ({ ...prev, page: false }));
      }
    };

    fetchData();
  }, [id, navigate]);

  const handleEquipmentUpdate = async (e) => {
    e.preventDefault();
    try {
      setLoading(prev => ({ ...prev, equipment: true }));
      await axios.put(
        `/api/equipment/${id}`,
        { name },
        getAuthHeader()
      );
      navigate('/manage-equipment');
    } catch (err) {
      setError(err.response?.data?.message || 'Ошибка сохранения оборудования');
    } finally {
      setLoading(prev => ({ ...prev, equipment: false }));
    }
  };

  const handleAddSensor = async () => {
    try {
      setLoading(prev => ({ ...prev, sensors: true }));
      const res = await axios.post(
        '/api/sensors/add',
        {
          name: newSensor.name,
          sensor_type_id: newSensor.typeId,
          data_source: newSensor.dataSource,
          equipment_id: id
        },
        getAuthHeader()
      );

      setSensors(prev => [...prev, res.data]);
      setNewSensor({ name: '', typeId: '', dataSource: '' });
    } catch (err) {
      setError(err.response?.data?.message || 'Ошибка добавления датчика');
    } finally {
      setLoading(prev => ({ ...prev, sensors: false }));
    }
  };

  const handleSaveEditedSensor = async () => {
    // 1. Проверяем, есть ли изменения
    const originalSensor = sensors.find(s => s.id === editingSensor.id);
    if (!originalSensor) {
      setError('Датчик не найден');
      return;
    }

    const hasChanges = (
      originalSensor.name !== editingSensor.name ||
      originalSensor.typeId !== editingSensor.typeId ||
      originalSensor.dataSource !== editingSensor.dataSource
    );

    if (!hasChanges) {
      setOpenEditDialog(false);
      return;
    }

    // 2. Отправляем только если есть изменения
    try {
      setLoading(prev => ({ ...prev, sensors: true }));
      
      const response = await axios.put(
        `/api/sensors/${editingSensor.id}`,
        {
          name: editingSensor.name,
          sensor_type_id: editingSensor.typeId,
          data_source: editingSensor.dataSource
        },
        getAuthHeader()
      );

      // 3. Обновляем состояние только после успешного ответа
      setSensors(prev => prev.map(s => 
        s.id === editingSensor.id ? {
          ...s,
          name: response.data.name,
          typeId: response.data.sensor_type_id,
          dataSource: response.data.data_source
        } : s
      ));
      
      setOpenEditDialog(false);
    } catch (err) {
      console.error('Ошибка сохранения датчика:', err);
      setError(err.response?.data?.message || 
              err.response?.data?.error || 
              'Ошибка сохранения датчика');
    } finally {
      setLoading(prev => ({ ...prev, sensors: false }));
    }
  };


  const handleRemoveSensor = async (sensorId) => {
    if (!window.confirm('Удалить датчик?')) return;
    try {
      setLoading(prev => ({ ...prev, sensors: true }));
      await axios.delete(`/api/sensors/${sensorId}`, getAuthHeader());
      setSensors(prev => prev.filter(s => s.id !== sensorId));
    } catch (err) {
      setError(err.response?.data?.message || 'Ошибка удаления датчика');
    } finally {
      setLoading(prev => ({ ...prev, sensors: false }));
    }
  };

  if (loading.page) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        <Button 
          variant="contained" 
          onClick={() => navigate('/manage-equipment')}
        >
          Вернуться к списку
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>Редактировать оборудование</Typography>
      
      <Box component="form" onSubmit={handleEquipmentUpdate} sx={{ mb: 4 }}>
        <TextField
          fullWidth
          label="Название оборудования"
          value={name}
          onChange={e => setName(e.target.value)}
          sx={{ mb: 2 }}
          required
        />
        <Button 
          variant="contained" 
          type="submit" 
          startIcon={loading.equipment ? <CircularProgress size={24} /> : <SaveIcon />}
          disabled={loading.equipment}
        >
          Сохранить оборудование
        </Button>
      </Box>

      <Typography variant="h6" gutterBottom>Датчики оборудования</Typography>
      
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Название</TableCell>
              <TableCell>Тип</TableCell>
              <TableCell>Источник данных</TableCell>
              <TableCell width="120px">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sensors.length > 0 ? (
              sensors.map((sensor) => (
                <TableRow key={sensor.id}>
                  <TableCell>{sensor.name}</TableCell>
                  <TableCell>
                    {sensorTypes.find(t => t.id === sensor.sensor_type_id)?.name || 'Неизвестный тип'}
                  </TableCell>
                  <TableCell>{sensor.data_source}</TableCell>
                  <TableCell>
                    <IconButton 
                      onClick={() => {
                        setEditingSensor({
                          id: sensor.id,
                          name: sensor.name,
                          typeId: sensor.sensor_type_id,
                          dataSource: sensor.data_source
                        });
                        setOpenEditDialog(true);
                      }}
                      disabled={loading.sensors}
                    >
                      <EditIcon color="primary" />
                    </IconButton>
                    <IconButton 
                      onClick={() => handleRemoveSensor(sensor.id)}
                      disabled={loading.sensors}
                    >
                      <DeleteIcon color="error" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  Нет подключенных датчиков
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="h6" gutterBottom>Добавить датчик</Typography>
      <Paper sx={{ p: 2, mb: 4 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
          <TextField
            label="Название датчика"
            value={newSensor.name}
            onChange={(e) => setNewSensor({...newSensor, name: e.target.value})}
            sx={{ flex: 2 }}
            required
          />
          
          <FormControl sx={{ flex: 1 }} required>
            <InputLabel>Тип датчика</InputLabel>
            <Select
              value={newSensor.typeId}
              label="Тип датчика"
              onChange={(e) => setNewSensor({...newSensor, typeId: e.target.value})}
            >
              {sensorTypes.map(type => (
                <MenuItem key={type.id} value={type.id}>
                  {type.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            label="Источник данных"
            value={newSensor.dataSource}
            onChange={(e) => setNewSensor({...newSensor, dataSource: e.target.value})}
            placeholder="sensor/a1"
            sx={{ flex: 2 }}
            required
          />
        </Box>
        <Button 
          variant="contained" 
          startIcon={loading.sensors ? <CircularProgress size={24} /> : <AddIcon />}
          onClick={handleAddSensor}
          disabled={loading.sensors || !newSensor.name || !newSensor.typeId || !newSensor.dataSource}
        >
          Добавить датчик
        </Button>
      </Paper>

      <Dialog open={openEditDialog} onClose={() => !loading.sensors && setOpenEditDialog(false)}>
        <DialogTitle>Редактировать датчик</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Название датчика"
              value={editingSensor?.name || ''}
              onChange={(e) => setEditingSensor({...editingSensor, name: e.target.value})}
              fullWidth
              required
            />
            
            <FormControl fullWidth required>
              <InputLabel>Тип датчика</InputLabel>
              <Select
                value={editingSensor?.typeId || ''}
                label="Тип датчика"
                onChange={(e) => setEditingSensor({...editingSensor, typeId: e.target.value})}
              >
                {sensorTypes.map(type => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="Источник данных"
              value={editingSensor?.dataSource || ''}
              onChange={(e) => setEditingSensor({...editingSensor, dataSource: e.target.value})}
              placeholder="sensor/a1"
              fullWidth
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setOpenEditDialog(false)} 
            startIcon={<CloseIcon />}
            disabled={loading.sensors}
          >
            Отмена
          </Button>
          <Button 
            onClick={handleSaveEditedSensor} 
            variant="contained" 
            startIcon={loading.sensors ? <CircularProgress size={24} /> : <SaveIcon />}
            disabled={loading.sensors || !editingSensor?.name || !editingSensor?.typeId || !editingSensor?.dataSource}
          >
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
