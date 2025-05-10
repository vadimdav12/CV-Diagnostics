// src/pages/EquipmentList.jsx

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Switch,
  Box,
  Grid,
  TextField
} from '@mui/material';
import { fetchEquipments } from '../api';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function EquipmentList() {
  const [equipments, setEquipments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortAsc, setSortAsc] = useState(true);
  const navigate = useNavigate();

  // Получаем userId из JWT
  const token = localStorage.getItem('access_token');
  const userId = token
    ? JSON.parse(atob(token.split('.')[1])).sub
      || JSON.parse(atob(token.split('.')[1])).id
    : null;

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchEquipments();
        setEquipments(res.data.map(eq => ({ ...eq, active: true })));
      } catch (err) {
        console.error('Ошибка загрузки оборудования', err);
      }
    })();
  }, []);

  const filtered = equipments
    .filter(eq => eq.name.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) =>
      sortAsc
        ? a.name.localeCompare(b.name)
        : b.name.localeCompare(a.name)
    );

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Выбор оборудования
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, px: 1 }}>
        <TextField
          label="Поиск"
          size="small"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <Paper
          component="button"
          onClick={() => setSortAsc(!sortAsc)}
          sx={{ p: 1, cursor: 'pointer' }}
        >
          Сортировка: {sortAsc ? '↑' : '↓'}
        </Paper>
      </Box>

      <Grid container spacing={2}>
        {filtered.map(eq => (
          <Grid item xs={12} key={eq.id}>
            <Paper
              onClick={async () => {
                try {
                  // Проверяем, есть ли у пользователя конфиг для этого оборудования
                  await axios.get(`/api/configuration/${userId}/${eq.id}`);
                  // Если есть — сразу на страницу визуализации
                  navigate(`/visualization/${eq.id}`);
                } catch (err) {
                  if (err.response?.status === 404) {
                    // Если нет — идём в конструктор для создания конфига
                    navigate('/configurator', { state: { equipmentId: eq.id } });
                  } else {
                    console.error('Ошибка при проверке конфигурации:', err);
                  }
                }
              }}
              sx={{
                p: 2,
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer'
              }}
            >
              <img
                src="/equipment-icon.png"
                alt="Иконка оборудования"
                style={{ width: 60, height: 60, marginRight: 16 }}
              />

              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6">{eq.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Датчики: тепловые, вибрационные, токовые
                </Typography>
              </Box>

              <Switch
                checked={eq.active}
                onChange={() =>
                  setEquipments(prev =>
                    prev.map(item =>
                      item.id === eq.id
                        ? { ...item, active: !item.active }
                        : item
                    )
                  )
                }
              />
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
