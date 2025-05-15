// frontend/src/pages/Configurator.jsx

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DraggableBlock from '../components/DraggableBlock.jsx';
import '../components/configurator.css';
import axios from 'axios';

/**
 * Начальные данные для панели перетаскивания:
 * - dataSources: единый блок "Датчик"
 * - functions и charts — без изменений
 */
const initialBlocks = {
  dataSources: [
    {
      id: 'sensor',
      label: 'Датчик',
      type: 'dataSource',
      parameters: { sensor_id: '', parameter_id: '', key: '' }
    }
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
  const navigate     = useNavigate();
  const location     = useLocation();
  const canvasRef    = useRef(null);
  const equipmentId  = location.state?.equipmentId;
  const token        = localStorage.getItem('access_token');
  const userId       = token
    ? (JSON.parse(atob(token.split('.')[1])).sub || JSON.parse(atob(token.split('.')[1])).id)
    : null;

  const [config, setConfig]                     = useState({ version: '1.0', blocks: {}, connections: [] });
  const [uiBlocks, setUiBlocks]                 = useState([]);
  const [connectingFrom, setConnectingFrom]     = useState(null);
  const [sensorsList, setSensorsList]           = useState([]);
  const [sensorTypesList, setSensorTypesList]   = useState([]);
  const [parametersList, setParametersList]     = useState([]);
  const [sensorParamsList, setSensorParamsList] = useState([]);
  const [selectedBlockUid, setSelectedBlockUid] = useState(null);

  // Устанавливаем JWT-токен для axios
  useEffect(() => {
    if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }, [token]);

  // Загружаем сенсоры, их типы и справочник параметров
  useEffect(() => {
    const sensorsUrl = equipmentId
      ? `/api/equipment/${equipmentId}/sensors`
      : '/api/sensors';
    axios.get(sensorsUrl)
      .then(res => {
        const list = Array.isArray(res.data) ? res.data : (res.data.sensors || []);
        setSensorsList(list);
      })
      .catch(console.error);

    // Список типов датчиков
    axios.get('/api/sensor-type')
      .then(res => setSensorTypesList(res.data))
      .catch(console.error);

    axios.get('/api/parameter')
      .then(res => {
        const list = Array.isArray(res.data) ? res.data : (res.data.parameters || []);
        setParametersList(list);
      })
      .catch(console.error);
  }, [equipmentId]);

  // Добавление блока на холст
  const handleDrop = e => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;
    const block = JSON.parse(data);
    const rect  = canvasRef.current.getBoundingClientRect();
    const uid   = `${block.type}_${Date.now()}`;
    const newBlock = {
      ...block,
      uid,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
    setUiBlocks(u => [...u, newBlock]);
    setConfig(c => ({
      ...c,
      blocks: { ...c.blocks, [uid]: { type: block.type, parameters: block.parameters } }
    }));
  };
  const handleDragStartFromPanel = (e, block) =>
    e.dataTransfer.setData('block', JSON.stringify(block));

  // Соединения между блоками
  const startConnection = id => setConnectingFrom(id);
  const completeConnection = id => {
    if (!connectingFrom || connectingFrom === id) return;
    const from = uiBlocks.find(b => b.uid === connectingFrom);
    const to   = uiBlocks.find(b => b.uid === id);
    const rules = { dataSource: ['function'], function: ['chart'], chart: [] };
    if (!rules[from.type].includes(to.type)) {
      alert('Неверное соединение');
    } else if (config.connections.some(c => c.source === connectingFrom)) {
      alert('Источник уже используется');
    } else if (config.connections.some(c => c.target === id)) {
      alert('Приемник уже занят');
    } else {
      setConfig(c => ({
        ...c,
        connections: [...c.connections, { source: connectingFrom, target: id }]
      }));
    }
    setConnectingFrom(null);
  };
  const renderArrows = () =>
    config.connections.map((c, i) => {
      const f = uiBlocks.find(b => b.uid === c.source);
      const t = uiBlocks.find(b => b.uid === c.target);
      if (!f || !t) return null;
      return (
        <line key={i}
              x1={f.x + 160} y1={f.y + 30}
              x2={t.x}       y2={t.y + 30}
              stroke="black" strokeWidth={2}
              markerEnd="url(#arrowhead)" />
      );
    });

  // Перетаскивание и удаление блоков
  const handleBlockDrag = (uid, dx, dy) =>
    setUiBlocks(u => u.map(b => b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b));
  const handleDeleteBlock = uid => {
    setUiBlocks(u => u.filter(b => b.uid !== uid));
    setConfig(c => ({
      ...c,
      blocks: Object.fromEntries(Object.entries(c.blocks).filter(([k]) => k !== uid)),
      connections: c.connections.filter(cn => cn.source !== uid && cn.target !== uid)
    }));
    if (selectedBlockUid === uid) setSelectedBlockUid(null);
  };

  // Выбор блока для редактирования
  const handleSelectBlock = uid => setSelectedBlockUid(uid);
  const selectedBlock = uiBlocks.find(b => b.uid === selectedBlockUid);

  // Изменение параметров выбранного блока
  const handleParamChange = (field, value) => {
    setUiBlocks(u => u.map(b => {
      if (b.uid !== selectedBlockUid) return b;
      const newParams = { ...b.parameters };
      let newLabel    = b.label;

      if (field === 'sensor_id') {
        newParams.sensor_id    = value;
        newParams.parameter_id = '';
        newParams.key          = '';
        // подтягиваем привязанные параметры
        axios.get(`/api/sensors_parameters/${value}`)
          .then(res => setSensorParamsList(res.data))
          .catch(() => setSensorParamsList([]));
        // обновляем метку: имя и тип датчика
        const s = sensorsList.find(s => s.id === value);
        if (s) {
          const typeObj = sensorTypesList.find(t => t.id === s.sensor_type_id);
          const typeName = typeObj ? typeObj.name : s.sensor_type_id;
          newLabel = `${s.name} (ID:${s.id}, ${typeName})`;
        }
      }

      if (field === 'parameter_id') {
        newParams.parameter_id = value;
        const sp = sensorParamsList.find(sp => sp.parameter_id === value);
        if (sp) newParams.key = sp.key;
      }

      return { ...b, parameters: newParams, label: newLabel };
    }));

    setConfig(c => ({
      ...c,
      blocks: {
        ...c.blocks,
        [selectedBlockUid]: {
          ...c.blocks[selectedBlockUid],
          parameters: {
            ...c.blocks[selectedBlockUid].parameters,
            [field]: value,
            ...(field === 'sensor_id' ? { parameter_id: '', key: '' } : {}),
            ...(field === 'parameter_id'
              ? { key: (sensorParamsList.find(sp => sp.parameter_id === value) || {}).key || '' }
              : {})
          }
        }
      }
    }));
  };

  const handleHomeClick  = () => navigate('/');
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
          <h3>Датчик</h3>
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
            <div key={b.id} className="block" draggable
                 onDragStart={e => handleDragStartFromPanel(e, b)}>
              {b.label}
            </div>
          ))}
          <h3>Графики</h3>
          {initialBlocks.charts.map(b => (
            <div key={b.id} className="block" draggable
                 onDragStart={e => handleDragStartFromPanel(e, b)}>
              {b.label}
            </div>
          ))}
        </aside>

        <section ref={canvasRef}
                 className="canvas"
                 onDrop={handleDrop}
                 onDragOver={e => e.preventDefault()}>
          <svg className="connections">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7"
                      refX="10" refY="3.5" orient="auto">
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
            <label>Сенсор</label>
            <select value={selectedBlock.parameters.sensor_id}
                    onChange={e => handleParamChange('sensor_id', Number(e.target.value))}>
              <option value="">— выберите —</option>
              {sensorsList.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Параметр</label>
            <select value={selectedBlock.parameters.parameter_id}
                    disabled={!selectedBlock.parameters.sensor_id}
                    onChange={e => handleParamChange('parameter_id', Number(e.target.value))}>
              <option value="">— выберите —</option>
              {sensorParamsList.map(sp => {
                const p = parametersList.find(p => p.id === sp.parameter_id);
                return (
                  <option key={sp.parameter_id} value={sp.parameter_id}>
                    {p ? p.name : `Param ${sp.parameter_id}`}
                  </option>
                );
              })}
            </select>
          </div>

          {selectedBlock.parameters.parameter_id && (
            <div className="field">
              <label>JSON-ключ</label>
              <input type="text" value={selectedBlock.parameters.key} readOnly />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
