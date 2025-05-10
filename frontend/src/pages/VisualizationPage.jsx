import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Container, Typography, Button, Grid, CircularProgress, Box
} from '@mui/material';
import axios from 'axios';
import {
  ResponsiveContainer, LineChart, Line,
  CartesianGrid, XAxis, YAxis, Tooltip, Legend
} from 'recharts';

export default function VisualizationPage() {
  const { equipmentId } = useParams();
  const navigate = useNavigate();

  // Получаем userId из JWT
  const token = localStorage.getItem('access_token');
  const userId = token
    ? JSON.parse(atob(token.split('.')[1])).sub
      || JSON.parse(atob(token.split('.')[1])).id
    : null;

  const [result, setResult] = useState({});
  const [loading, setLoading] = useState(true);
  const [noConfig, setNoConfig] = useState(false);

  useEffect(() => {
    if (!userId) {
      navigate('/login', { replace: true });
      return;
    }
    (async () => {
      try {
        await axios.get(`/api/configuration/${userId}/${equipmentId}`);
      } catch (err) {
        if (err.response?.status === 404) {
          setNoConfig(true);
          setLoading(false);
          return;
        }
      }
      const { data } = await axios.get(
        `/api/configuration/${userId}/${equipmentId}/apply`
      );
      setResult(data.result || {});
      setLoading(false);
    })();
  }, [userId, equipmentId, navigate]);

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
          const data = x_values.map((x, i) => ({ x, y: y_values[i] }));
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
                    dot={false}
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
