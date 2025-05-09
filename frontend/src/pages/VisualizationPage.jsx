import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button, Container, Typography } from '@mui/material';
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export default function VisualizationPage() {
  const { state: config } = useLocation();
  const navigate = useNavigate();

  // Если попали без конфига — вернём на конфигуратор
  if (!config) {
    navigate('/configurator', { replace: true });
    return null;
  }

  // Извлекаем функцию и тип графика из конфига
  const functionName = config.blocks[
    config.connections[0].target
  ].parameters.function;           // например "fourier"
  const chartType = config.blocks[
    config.connections[1].target
  ].parameters.chart_type;         // "time" или "frequency"

  // Генерируем синтетический сигнал и/или спектр
  const data = useMemo(() => {
    const fs = 1000;                // частота дискретизации
    const N = fs;                  // 1 секунда
    const t = Array.from({ length: N }, (_, i) => i / fs);
    // сигнал: 50 Гц + 120 Гц
    const signal = t.map(
      time => Math.sin(2 * Math.PI * 50 * time) + 0.5 * Math.sin(2 * Math.PI * 120 * time)
    );

    if (chartType === 'time') {
      return t.map((time, i) => ({ x: time, y: signal[i] }));
    } else {
      // спектр Фурье
      const re = [], im = [];
      for (let k = 0; k < N; k++) {
        // простейшая DFT, для наглядности — не оптимально
        let sumRe = 0, sumIm = 0;
        for (let n = 0; n < N; n++) {
          const angle = (2 * Math.PI * k * n) / N;
          sumRe +=  signal[n] * Math.cos(angle);
          sumIm += -signal[n] * Math.sin(angle);
        }
        re.push(sumRe);
        im.push(sumIm);
      }
      const freqs = Array.from({ length: N/2 }, (_, k) => k * fs / N);
      return freqs.map((f, k) => ({
        x: f,
        y: Math.sqrt(re[k]**2 + im[k]**2)
      }));
    }
  }, [chartType]);

  return (
    <Container sx={{ mt: 4, height: 500 }}>
      <Typography variant="h4" gutterBottom>
        Визуализация: {functionName} → {chartType}
      </Typography>

      <ResponsiveContainer width="100%" height="80%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="x"
            name={chartType === 'time' ? 'Время (с)' : 'Частота (Гц)'}
            tickFormatter={val => chartType === 'time' ? val.toFixed(2) : val}
          />
          <YAxis />
          <Tooltip
            labelFormatter={label =>
              chartType === 'time'
                ? `t = ${label.toFixed(3)} с`
                : `f = ${label.toFixed(1)} Гц`
            }
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="y"
            stroke="#1976d2"
            dot={false}
            name={chartType === 'time' ? 'Амплитуда' : 'Спектральная амплитуда'}
          />
        </LineChart>
      </ResponsiveContainer>

      <Button sx={{ mt: 2 }} variant="contained" onClick={() => navigate('/')}>
        Назад
      </Button>
    </Container>
  );
}
