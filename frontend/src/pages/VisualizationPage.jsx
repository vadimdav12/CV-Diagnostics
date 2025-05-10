import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button, Container, Typography } from '@mui/material';
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export default function VisualizationPage() {
  const { state: config } = useLocation();
  const navigate = useNavigate();

  // Проверяем наличие конфигурации
  const hasConfig = config && Array.isArray(config.connections) && config.connections.length > 0;

  // Извлекаем параметры функции и типа графика, если есть
  let functionName = '';
  let chartType = '';
  if (hasConfig) {
    const funcTarget = config.connections[0].target;
    const chartTarget = config.connections[1].target;
    functionName = config.blocks[funcTarget].parameters.function;
    chartType = config.blocks[chartTarget].parameters.chart_type;
  }

  // Подготовка данных для графика
  const data = useMemo(() => {
    if (!hasConfig) return [];

    const fs = 1000; // частота дискретизации
    const N = fs;    // 1 секунда данных
    const t = Array.from({ length: N }, (_, i) => i / fs);
    const signal = t.map(
      time => Math.sin(2 * Math.PI * 50 * time) + 0.5 * Math.sin(2 * Math.PI * 120 * time)
    );

    if (chartType === 'time') {
      return t.map((time, i) => ({ x: time, y: signal[i] }));
    } else {
      // примитивный DFT для наглядности
      const re = new Array(N).fill(0);
      const im = new Array(N).fill(0);
      for (let k = 0; k < N; k++) {
        for (let n = 0; n < N; n++) {
          const angle = (2 * Math.PI * k * n) / N;
          re[k] +=  signal[n] * Math.cos(angle);
          im[k] += -signal[n] * Math.sin(angle);
        }
      }
      const freqs = Array.from({ length: N / 2 }, (_, k) => k * fs / N);
      return freqs.map((f, k) => ({ x: f, y: Math.sqrt(re[k]**2 + im[k]**2) }));
    }
  }, [hasConfig, chartType]);

  return (
    <Container sx={{ mt: 4, height: 500 }}>
      {hasConfig ? (
        <>
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
        </>
      ) : (
        <Typography variant="h5" align="center" sx={{ mt: 4 }}>
          Пожалуйста, настройте no-code конфигуратор для выбранного оборудования.
        </Typography>
      )}

      <Button sx={{ mt: 2 }} variant="contained" onClick={() => navigate('/configurator')}>
        Открыть no-code конфигуратор
      </Button>
    </Container>
  );
}
