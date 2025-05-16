// frontend/src/pages/VisualizationPage.jsx

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams }           from 'react-router-dom';
import {
  Container, Typography, Button,
  Grid, CircularProgress, Box
} from '@mui/material';
import axios                                from 'axios';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';

export default function VisualizationPage() {
  const { equipmentId } = useParams();
  const navigate        = useNavigate();

  // Устанавливаем заголовок авторизации, если есть токен
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  const [result, setResult]     = useState({});
  const [loading, setLoading]   = useState(true);
  const [noConfig, setNoConfig] = useState(false);

  // хранит последний ISO timestamp, чтобы back-end понимал, с какого момента отдавать
  const lastUpdateRef = useRef(null);

  useEffect(() => {
    let intervalId;

    // инициализируем last_update текущим временем
    lastUpdateRef.current = new Date().toISOString();

    const fetchData = async () => {
      try {
        const params = `?last_update=${encodeURIComponent(lastUpdateRef.current)}`;
        const res = await axios.get(
          `/api/configuration/1/${equipmentId}/apply${params}`
        );
        const data = res.data.result || {};
        setResult(data);
        setLoading(false);

        // обновляем last_update на самое позднее значение из каждого блока
        Object.values(data).forEach(block => {
          const xs = block.x_values;
          if (xs && xs.length) {
            lastUpdateRef.current = xs[xs.length - 1];
          }
        });
      } catch (err) {
        if (err.response?.status === 404) {
          setNoConfig(true);
          setLoading(false);
        } else {
          console.error('Ошибка при получении данных:', err);
        }
      }
    };

    // проверка существования конфигурации и запуск опроса
    axios.get(`/api/configuration/1/${equipmentId}`)
      .then(() => {
        fetchData();                  // первый запрос сразу
        intervalId = setInterval(fetchData, 5000); // затем каждые 5 сек
      })
      .catch(err => {
        if (err.response?.status === 404) {
          setNoConfig(true);
          setLoading(false);
        } else {
          console.error(err);
        }
      });

    return () => clearInterval(intervalId);
  }, [equipmentId]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (noConfig) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="h5">
          Для этого оборудования ещё нет настроек.
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/configurator', { state: { equipmentId } })}
          sx={{ mt: 2 }}
        >
          Открыть no-code конфигуратор
        </Button>
      </Container>
    );
  }

  const charts = Object.entries(result);

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Результаты оборудования #{equipmentId}
      </Typography>

      <Grid container spacing={4}>
        {charts.length === 0 && (
          <Typography>Нет данных для отображения графиков.</Typography>
        )}
        {charts.map(([blockId, { x_values, y_values }]) => {
          // Ограничиваем максимум 200 последних точек
          const total = x_values.length;
          const start = Math.max(0, total - 200);
          const xs = x_values.slice(start);
          const ys = y_values.slice(start);
          const data = xs.map((x, i) => ({ x, y: ys[i] }));

          return (
            <Grid item xs={12} md={6} key={blockId}>
              <Typography variant="h6">Блок {blockId}</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="x" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="y"
                    name="Значение"
                    stroke="blue"     // синяя линия
                    dot={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Grid>
          );
        })}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Button
          variant="outlined"
          onClick={() => navigate('/configurator', { state: { equipmentId } })}
        >
          Изменить настройки
        </Button>
      </Box>
    </Container>
  );
}
