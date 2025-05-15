// frontend/src/pages/Configurator.jsx

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DraggableBlock from '../components/DraggableBlock.jsx';
import '../components/configurator.css';
import axios from 'axios';

/**
 * Начальные данные для панели перетаскивания:
 * - dataSources: единый блок "Датчик"
 * - functions, charts — без изменений
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
    { id: 'func1', label: 'Фурье',  type: 'function', parameters: { function: 'spectrum' } },
    { id: 'func2', label: 'Фильтр', type: 'function', parameters: { function: 'lowpass' } }
  ],
  charts: [
    { id: 'chart1', label: 'Временной график',  type: 'chart', parameters: { chart_type: 'time' } },
    { id: 'chart2', label: 'Частотный график',  type: 'chart', parameters: { chart_type: 'frequency' } }
  ]
};

/**
 * Формирует текстовый label для блока в зависимости от его типа и параметров
 */
function deriveLabel(block, sensorsList, sensorTypesList) {
  if (block.type === 'dataSource') {
    const s = sensorsList.find(s => s.id === block.parameters.sensor_id);
    if (!s) return 'Датчик';
    const t = sensorTypesList.find(t => t.id === s.sensor_type_id);
    const typeName = t ? t.name : s.sensor_type_id;
    return `${s.name} (ID:${s.id}, ${typeName})`;
  }
  if (block.type === 'function') {
    const f = initialBlocks.functions.find(f => f.parameters.function === block.parameters.function);
    return f ? f.label : block.parameters.function;
  }
  if (block.type === 'chart') {
    const c = initialBlocks.charts.find(c => c.parameters.chart_type === block.parameters.chart_type);
    return c ? c.label : block.parameters.chart_type;
  }
  return '';
}

export default function Configurator() {
  const navigate    = useNavigate();
  const location    = useLocation();
  const canvasRef   = useRef(null);
  const equipmentId = location.state?.equipmentId;
  const token       = localStorage.getItem('access_token');
  const userId      = token
    ? (JSON.parse(atob(token.split('.')[1])).sub || JSON.parse(atob(token.split('.')[1])).id)
    : null;

  // Основное состояние
  const [config, setConfig]                     = useState({ version: '1.0', blocks: {}, connections: [] });
  const [uiBlocks, setUiBlocks]                 = useState([]);
  const [sensorsList, setSensorsList]           = useState([]);
  const [sensorTypesList, setSensorTypesList]   = useState([]);
  const [parametersList, setParametersList]     = useState([]);
  const [sensorParamsList, setSensorParamsList] = useState([]);
  const [selectedBlockUid, setSelectedBlockUid] = useState(null);

  // Состояние для временной стрелки при drag-to-connect
  const [draggingArrow, setDraggingArrow] = useState(null);
  // { fromUid, x1, y1, x2, y2 }

  // Устанавливаем JWT-токен для axios
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  // Загружаем справочники: датчики, их типы, параметры
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

  // При входе загружаем сохранённую конфигурацию и восстанавливаем uiBlocks
  useEffect(() => {
    if (!userId || !equipmentId) return;
    axios.get(`/api/configuration/${userId}/${equipmentId}`)
      .then(res => {
        const saved = res.data.config;
        setConfig(saved);
        const blocksArr = Object.entries(saved.blocks).map(([uid, b], idx) => ({
          uid,
          type: b.type,
          parameters: b.parameters,
          label: deriveLabel(b, sensorsList, sensorTypesList),
          x: typeof b.x === 'number' ? b.x : 20,
          y: typeof b.y === 'number' ? b.y : 20 + idx * 100
        }));
        setUiBlocks(blocksArr);
      })
      .catch(err => {
        if (err.response?.status !== 404) console.error(err);
      });
  }, [userId, equipmentId, sensorsList, sensorTypesList]);

  // Добавление блока на холст drag-and-drop
  const handleDrop = e => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;
    const block = JSON.parse(data);
    const rect  = canvasRef.current.getBoundingClientRect();
    const uid   = `${block.type}_${Date.now()}`;
    const x     = e.clientX - rect.left;
    const y     = e.clientY - rect.top;
    const newBlock = { ...block, uid, x, y, label: block.label };
    setUiBlocks(u => [...u, newBlock]);
    setConfig(c => ({
      ...c,
      blocks: {
        ...c.blocks,
        [uid]: { type: block.type, parameters: block.parameters, x, y }
      }
    }));
  };
  const handleDragStartFromPanel = (e, b) =>
    e.dataTransfer.setData('block', JSON.stringify(b));

  // Начало drag-to-connect: заводим временную стрелку
  const handleStartArrow = (fromUid, clientX, clientY) => {
    const rect = canvasRef.current.getBoundingClientRect();
    setDraggingArrow({
      fromUid,
      x1: clientX - rect.left,
      y1: clientY - rect.top,
      x2: clientX - rect.left,
      y2: clientY - rect.top
    });
  };

  // Обновление координат временной стрелки при движении мыши
  const handleCanvasMouseMove = e => {
    if (!draggingArrow) return;
    const rect = canvasRef.current.getBoundingClientRect();
    setDraggingArrow(a => ({
      ...a,
      x2: e.clientX - rect.left,
      y2: e.clientY - rect.top
    }));
  };

  // Завершение drag-to-connect: пытаемся соединить
  const handleCanvasMouseUp = e => {
    if (!draggingArrow) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const localX = e.clientX - rect.left;
    const localY = e.clientY - rect.top;
    const { fromUid } = draggingArrow;

    // Находим блок, в который отпустили внутри его прямоугольника
    const target = uiBlocks.find(b =>
      localX >= b.x && localX <= b.x + 160 &&
      localY >= b.y && localY <= b.y + 60
    );
    if (target && target.uid !== fromUid) {
      const fromBlock = uiBlocks.find(b => b.uid === fromUid);
      const rules = {
        dataSource: ['function', 'chart'],
        function: ['chart'],
        chart: []
      };
      if (
        rules[fromBlock.type].includes(target.type) &&
        !config.connections.some(c => c.source === fromUid) &&
        !config.connections.some(c => c.target === target.uid)
      ) {
        setConfig(c => ({
          ...c,
          connections: [...c.connections, { source: fromUid, target: target.uid }]
        }));
      }
    }
    setDraggingArrow(null);
  };

  // Рендер сохранённых соединений
  const renderArrows = () =>
    config.connections.map((c, i) => {
      const f = uiBlocks.find(b => b.uid === c.source);
      const t = uiBlocks.find(b => b.uid === c.target);
      if (!f || !t) return null;
      return (
        <line
          key={i}
          x1={f.x + 160} y1={f.y + 30}
          x2={t.x}       y2={t.y + 30}
          stroke="black"
          strokeWidth={2}
          markerEnd="url(#arrowhead)"
        />
      );
    });

  // Рендер временной стрелки (сплошная чёрная)
  const renderTempArrow = () =>
    draggingArrow && (
      <line
        x1={draggingArrow.x1} y1={draggingArrow.y1}
        x2={draggingArrow.x2} y2={draggingArrow.y2}
        stroke="black"
        strokeWidth={2}
      />
    );

  // Перетаскивание блока
  const handleBlockDrag = (uid, dx, dy) => {
    setUiBlocks(u => u.map(b =>
      b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b
    ));
    setConfig(c => ({
      ...c,
      blocks: {
        ...c.blocks,
        [uid]: {
          ...c.blocks[uid],
          x: c.blocks[uid].x + dx,
          y: c.blocks[uid].y + dy
        }
      }
    }));
  };

  // Удаление блока
  const handleDeleteBlock = uid => {
    setUiBlocks(u => u.filter(b => b.uid !== uid));
    setConfig(c => ({
      ...c,
      blocks: Object.fromEntries(
        Object.entries(c.blocks).filter(([k]) => k !== uid)
      ),
      connections: c.connections.filter(cn => cn.source !== uid && cn.target !== uid)
    }));
    if (selectedBlockUid === uid) setSelectedBlockUid(null);
  };

  // Выбор блока для редактирования
  const handleSelectBlock = uid => setSelectedBlockUid(uid);
  const selectedBlock = uiBlocks.find(b => b.uid === selectedBlockUid);

  // Обработка изменения параметров в панеле свойств
  const handleParamChange = (field, value) => {
    // Обновляем uiBlocks
    setUiBlocks(u => u.map(b => {
      if (b.uid !== selectedBlockUid) return b;
      const np = { ...b.parameters };
      let nl = b.label;
      if (field === 'sensor_id') {
        np.sensor_id = value;
        np.parameter_id = '';
        np.key = '';
        axios.get(`/api/sensors_parameters/${value}`)
          .then(r => setSensorParamsList(r.data))
          .catch(() => setSensorParamsList([]));
        const s = sensorsList.find(s => s.id === value);
        if (s) {
          const t = sensorTypesList.find(t => t.id === s.sensor_type_id);
          nl = `${s.name} (ID:${s.id}, ${t ? t.name : s.sensor_type_id})`;
        }
      }
      if (field === 'parameter_id') {
        np.parameter_id = value;
        const sp = sensorParamsList.find(sp => sp.parameter_id === value);
        if (sp) np.key = sp.key;
      }
      return { ...b, parameters: np, label: nl };
    }));

    // Обновляем config
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

  // Навигация и сохранение
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
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          onMouseLeave={handleCanvasMouseUp}
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
            {renderTempArrow()}
          </svg>

          {uiBlocks.map(b => (
            <DraggableBlock
              key={b.uid}
              block={b}
              onDrag={handleBlockDrag}
              onDelete={handleDeleteBlock}
              onClick={() => handleSelectBlock(b.uid)}
              onStartArrow={handleStartArrow}
            />
          ))}
        </section>
      </div>

      {selectedBlock && selectedBlock.type === 'dataSource' && (
        <div className="properties-panel">
          <h4>Настройки датчика</h4>

          <div className="field">
            <label>Сенсор:</label>
            <select
              value={selectedBlock.parameters.sensor_id}
              onChange={e => handleParamChange('sensor_id', Number(e.target.value))}
            >
              <option value="">— выберите сенсор —</option>
              {sensorsList.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Параметр:</label>
            <select
              value={selectedBlock.parameters.parameter_id}
              disabled={!selectedBlock.parameters.sensor_id}
              onChange={e => handleParamChange('parameter_id', Number(e.target.value))}
            >
              <option value="">— выберите параметр —</option>
              {sensorParamsList.map(sp => {
                const p = parametersList.find(p => p.id === sp.parameter_id);
                return (
                  <option key={sp.parameter_id} value={sp.parameter_id}>
                    {p ? p.name : `Параметр ${sp.parameter_id}`}
                  </option>
                );
              })}
            </select>
          </div>

          {selectedBlock.parameters.parameter_id && (
            <div className="field">
              <label>JSON-ключ:</label>
              <input type="text" value={selectedBlock.parameters.key} readOnly />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
