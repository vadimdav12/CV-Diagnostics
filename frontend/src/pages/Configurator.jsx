// frontend/src/pages/Configurator.jsx

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DraggableBlock from '../components/DraggableBlock.jsx';
import '../components/configurator.css';
import axios from 'axios';

/**
 * Начальные данные для блоков, разделенные по категориям:
 * - dataSources: датчики (источники данных)
 * - functions: функции обработки данных
 * - charts: графики для визуализации
 */
const initialBlocks = {
  dataSources: [
    { id: 'sensor1', label: 'Тепловой датчик', type: 'dataSource', parameters: { sensor_id: 1, parameter_id: 1, key: '' } },
    { id: 'sensor2', label: 'Вибро датчик', type: 'dataSource', parameters: { sensor_id: 2, parameter_id: 1, key: '' } },
    { id: 'sensor3', label: 'Токовый датчик', type: 'dataSource', parameters: { sensor_id: 3, parameter_id: 1, key: '' } }
  ],
  functions: [
    { id: 'func1', label: 'Фурье', type: 'function', parameters: { function: 'spectrum' } },
    { id: 'func2', label: 'Фильтр', type: 'function', parameters: { function: 'lowpass' } }
  ],
  charts: [
    { id: 'chart1', label: 'Временной график', type: 'chart', parameters: { chart_type: 'time' } },
    { id: 'chart2', label: 'Частотный график', type: 'chart', parameters: { chart_type: 'frequency' } }
  ]
};

export default function Configurator() {
  const navigate = useNavigate();
  const location = useLocation();
  const canvasRef = useRef(null);

  const equipmentId = location.state?.equipmentId;
  const token = localStorage.getItem('access_token');
  const userId = token
    ? (JSON.parse(atob(token.split('.')[1])).sub || JSON.parse(atob(token.split('.')[1])).id)
    : null;

  const [config, setConfig] = useState({ version: '1.0', blocks: {}, connections: [] });
  const [uiBlocks, setUiBlocks] = useState([]);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const [sensorsList, setSensorsList] = useState([]);
  const [parametersList, setParametersList] = useState([]);
  const [selectedBlockUid, setSelectedBlockUid] = useState(null);

  // Устанавливаем JWT-токен в axios
  useEffect(() => {
    if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }, [token]);

  // Загружаем сенсоры и параметры
  useEffect(() => {
    const sensorsUrl = equipmentId
      ? `/api/equipment/${equipmentId}/sensors`
      : '/api/sensors';
    axios.get(sensorsUrl)
      .then(res => {
        const data = res.data;
        setSensorsList(Array.isArray(data) ? data : (data.sensors || []));
      })
      .catch(console.error);

    axios.get('/api/parameter')
      .then(res => {
        const data = res.data;
        setParametersList(Array.isArray(data) ? data : (data.parameters || []));
      })
      .catch(console.error);
  }, [equipmentId]);

  // Добавление блока на canvas
  const handleDrop = e => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;
    const block = JSON.parse(data);
    const rect = canvasRef.current.getBoundingClientRect();
    const uid = `${block.type}_${Date.now()}`;
    const newBlock = {
      ...block,
      uid,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
    setUiBlocks(prev => [...prev, newBlock]);
    setConfig(prev => ({
      ...prev,
      blocks: {
        ...prev.blocks,
        [uid]: { type: block.type, parameters: block.parameters }
      }
    }));
  };

  const handleDragStartFromPanel = (e, block) => {
    e.dataTransfer.setData('block', JSON.stringify(block));
  };

  // Начало и завершение соединения
  const startConnection = fromId => setConnectingFrom(fromId);
  const completeConnection = toId => {
    if (!connectingFrom || connectingFrom === toId) return;
    const from = uiBlocks.find(b => b.uid === connectingFrom);
    const to = uiBlocks.find(b => b.uid === toId);
    const rules = { dataSource: ['function'], function: ['chart'], chart: [] };
    if (!rules[from.type].includes(to.type)) {
      alert('Неверное соединение');
    } else if (config.connections.some(c => c.source === connectingFrom)) {
      alert('Источник уже используется');
    } else if (config.connections.some(c => c.target === toId)) {
      alert('Приемник уже занят');
    } else {
      setConfig(prev => ({
        ...prev,
        connections: [...prev.connections, { source: connectingFrom, target: toId }]
      }));
    }
    setConnectingFrom(null);
  };

  // Отрисовка стрелок между блоками
  const renderArrows = () => config.connections.map((c, i) => {
    const f = uiBlocks.find(b => b.uid === c.source);
    const t = uiBlocks.find(b => b.uid === c.target);
    if (!f || !t) return null;
    return (
      <line
        key={i}
        x1={f.x + 160} y1={f.y + 30}
        x2={t.x}    y2={t.y + 30}
        stroke="black"
        strokeWidth={2}
        markerEnd="url(#arrowhead)"
      />
    );
  });

  const handleBlockDrag = (uid, dx, dy) => {
    setUiBlocks(prev =>
      prev.map(b => b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b)
    );
  };

  const handleDeleteBlock = uid => {
    setUiBlocks(prev => prev.filter(b => b.uid !== uid));
    setConfig(prev => ({
      ...prev,
      blocks: Object.fromEntries(
        Object.entries(prev.blocks).filter(([k]) => k !== uid)
      ),
      connections: prev.connections.filter(c => c.source !== uid && c.target !== uid)
    }));
    if (selectedBlockUid === uid) setSelectedBlockUid(null);
  };

  // Выбор блока для редактирования свойств
  const handleSelectBlock = uid => setSelectedBlockUid(uid);

  // Редактирование параметров выбранного блока
  const selectedBlock = uiBlocks.find(b => b.uid === selectedBlockUid);
  const handleParamChange = (field, value) => {
    // Обновляем uiBlocks
    setUiBlocks(prev =>
      prev.map(b =>
        b.uid === selectedBlockUid
          ? { ...b, parameters: { ...b.parameters, [field]: value } }
          : b
      )
    );
    // Обновляем config
    setConfig(prev => ({
      ...prev,
      blocks: {
        ...prev.blocks,
        [selectedBlockUid]: {
          ...prev.blocks[selectedBlockUid],
          parameters: {
            ...prev.blocks[selectedBlockUid].parameters,
            [field]: value
          }
        }
      }
    }));
  };

  const handleHomeClick = () => navigate('/');
  const handleApplyClick = async () => {
    if (!userId || !equipmentId) {
      alert('Нет userId или equipmentId');
      return;
    }
    try {
      await axios.get(`/api/configuration/${userId}/${equipmentId}`);
      await axios.put(`/api/configuration/${userId}/${equipmentId}`, config);
    } catch (err) {
      if (err.response?.status === 404) {
        await axios.post(`/api/configuration/${userId}/${equipmentId}`, config);
      } else {
        console.error(err);
        alert('Ошибка сохранения');
        return;
      }
    }
    navigate(`/visualization/${equipmentId}`);
  };

  return (
    <div className="configurator">
      <header className="top-bar">
        <div className="header-content">
          <span>No-code конфигуратор</span>
          <div className="header-buttons">
            <button onClick={handleHomeClick}>Домой</button>
            <button onClick={handleApplyClick}>Применить изменения</button>
          </div>
        </div>
      </header>

      <div className="main">
        <aside className="sidebar">
          <h3>Датчики</h3>
          {initialBlocks.dataSources.map(b => (
            <div
              key={b.id}
              className="block"
              draggable
              onDragStart={e => handleDragStartFromPanel(e, b)}
            >
              {b.label}
            </div>
          ))}
          <h3>Функции</h3>
          {initialBlocks.functions.map(b => (
            <div
              key={b.id}
              className="block"
              draggable
              onDragStart={e => handleDragStartFromPanel(e, b)}
            >
              {b.label}
            </div>
          ))}
          <h3>Графики</h3>
          {initialBlocks.charts.map(b => (
            <div
              key={b.id}
              className="block"
              draggable
              onDragStart={e => handleDragStartFromPanel(e, b)}
            >
              {b.label}
            </div>
          ))}
        </aside>

        <section
          ref={canvasRef}
          className="canvas"
          onDrop={handleDrop}
          onDragOver={e => e.preventDefault()}
        >
          <svg className="connections">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="10"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0,10 3.5,0 7" />
              </marker>
            </defs>
            {renderArrows()}
          </svg>

          {uiBlocks.map(b => (
            <DraggableBlock
              key={b.uid}
              block={b}
              onDrag={handleBlockDrag}
              onStartConnection={startConnection}
              onCompleteConnection={completeConnection}
              onDelete={handleDeleteBlock}
              onClick={() => handleSelectBlock(b.uid)}
            />
          ))}
        </section>
      </div>

      {selectedBlock && selectedBlock.type === 'dataSource' && (
        <div className="properties-panel">
          <h4>Настройки датчика</h4>
          <div className="field">
            <label>Датчик:</label>
            <select
              value={selectedBlock.parameters.sensor_id}
              onChange={e => handleParamChange('sensor_id', Number(e.target.value))}
            >
              <option value="">— выберите датчик —</option>
              {sensorsList.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name || `Sensor ${s.id}`}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Параметр:</label>
            <select
              value={selectedBlock.parameters.parameter_id}
              onChange={e => handleParamChange('parameter_id', Number(e.target.value))}
            >
              <option value="">— выберите параметр —</option>
              {parametersList.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name || `Param ${p.id}`}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>JSON-ключ:</label>
            <input type="text" value={selectedBlock.parameters.key} readOnly />
          </div>
        </div>
      )}
    </div>
  );
}
