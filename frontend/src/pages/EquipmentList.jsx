import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Switch,
  Box,
  Grid,
  TextField,
  Button
} from '@mui/material';
import { fetchEquipments } from '../api';

export default function EquipmentList() {
  const [equipments, setEquipments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    loadEquipments();
  }, []);

  const loadEquipments = async () => {
    try {
      const res = await fetchEquipments();
      // добавляем поле active по умолчанию true
      const initial = res.data.map(eq => ({ ...eq, active: true }));
      setEquipments(initial);
    } catch (error) {
      console.error('Ошибка загрузки оборудования', error);
    }
  };

  const handleToggle = (id) => {
    setEquipments(prev =>
      prev.map(eq =>
        eq.id === id ? { ...eq, active: !eq.active } : eq
      )
    );
  };

  // поиск + сортировка
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

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          mb: 2,
          px: 1
        }}
      >
        <TextField
          label="Поиск"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <Button onClick={() => setSortAsc(!sortAsc)}>
          Сортировка: {sortAsc ? 'по возрастанию' : 'по убыванию'}
        </Button>
      </Box>

      <Grid container spacing={2}>
        {filtered.map(eq => (
          <Grid item xs={12} key={eq.id}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                alignItems: 'center'
              }}
            >
              {/* Иконка. Можно заменить src на динамический URL из eq */}
              <img
                src="/equipment-icon.png"
                alt="Иконка оборудования"
                style={{
                  width: 60,
                  height: 60,
                  marginRight: 16
                }}
              />

              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6">{eq.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Датчики: тепловые, вибрационные, токовые
                </Typography>
              </Box>

              <Switch
                checked={eq.active}
                onChange={() => handleToggle(eq.id)}
              />
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
