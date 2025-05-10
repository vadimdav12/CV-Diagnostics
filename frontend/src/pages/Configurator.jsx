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
    { id: 'sensor1', label: 'Тепловой датчик', type: 'dataSource', parameters: { sensor_id: 1, parameter_id: 1 } },
    { id: 'sensor2', label: 'Вибро датчик', type: 'dataSource', parameters: { sensor_id: 2, parameter_id: 1 } },
    { id: 'sensor3', label: 'Токовый датчик', type: 'dataSource', parameters: { sensor_id: 3, parameter_id: 1 } }
  ],
  functions: [
    { id: 'func1', label: 'Фурье', type: 'function', parameters: { function: 'spectrum' } },
    { id: 'func2', label: 'Фильтр', type: 'function', parameters: { function: 'func1' } }
  ],
  charts: [
    { id: 'chart1', label: 'Временной график', type: 'chart', parameters: { chart_type: 'time' } },
    { id: 'chart2', label: 'Частотный график', type: 'chart', parameters: { chart_type: 'frequency' } }
  ]
};

/**
 * Основной компонент NoCode-конфигуратора
 */
const Configurator = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Получаем equipmentId из state (пришел из EquipmentList)
  const equipmentId = location.state?.equipmentId;

  // Получаем userId из JWT
  const token = localStorage.getItem('access_token');
  const userId = token
    ? (JSON.parse(atob(token.split('.')[1])).sub || JSON.parse(atob(token.split('.')[1])).id)
    : null;

  // Конфигурация (blocks + connections)
  const [config, setConfig] = useState({ version: '1.0', blocks: {}, connections: [] });
  const [uiBlocks, setUiBlocks] = useState([]);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const canvasRef = useRef(null);

  // Drop из панели
  const handleDrop = e => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;
    const block = JSON.parse(data);
    const rect = canvasRef.current.getBoundingClientRect();
    const uid = `${block.type}_${Date.now()}`;
    const newBlock = { ...block, uid, x: e.clientX - rect.left, y: e.clientY - rect.top };
    setUiBlocks(prev => [...prev, newBlock]);
    setConfig(prev => ({
      ...prev,
      blocks: { ...prev.blocks, [uid]: { type: block.type, parameters: block.parameters } }
    }));
  };

  const handleDragStartFromPanel = (e, block) => {
    e.dataTransfer.setData('block', JSON.stringify(block));
  };

  const startConnection = fromId => setConnectingFrom(fromId);

  const completeConnection = toId => {
    if (!connectingFrom || connectingFrom === toId) return;
    const from = uiBlocks.find(b => b.uid === connectingFrom);
    const to = uiBlocks.find(b => b.uid === toId);
    if (!from || !to) return;
    const rules = { dataSource: ['function'], function: ['chart'], chart: [] };
    if (!rules[from.type].includes(to.type)) {
      alert('Неверное соединение');
    } else if (config.connections.some(c => c.source === connectingFrom)) {
      alert('Источник уже используется');
    } else if (config.connections.some(c => c.target === toId)) {
      alert('Приемник уже занят');
    } else {
      setConfig(prev => ({ ...prev, connections: [...prev.connections, { source: connectingFrom, target: toId }] }));
    }
    setConnectingFrom(null);
  };

  const renderArrows = () => config.connections.map((c, i) => {
    const f = uiBlocks.find(b => b.uid === c.source);
    const t = uiBlocks.find(b => b.uid === c.target);
    if (!f || !t) return null;
    return <line key={i} x1={f.x + 160} y1={f.y + 30} x2={t.x} y2={t.y + 30}
      stroke="black" strokeWidth={2} markerEnd="url(#arrowhead)" />;
  });

  const handleBlockDrag = (uid, dx, dy) => {
    setUiBlocks(prev => prev.map(b => b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b));
  };

  const handleDeleteBlock = uid => {
    setUiBlocks(prev => prev.filter(b => b.uid !== uid));
    setConfig(prev => ({
      ...prev,
      blocks: Object.fromEntries(Object.entries(prev.blocks).filter(([k]) => k !== uid)),
      connections: prev.connections.filter(c => c.source !== uid && c.target !== uid)
    }));
  };

  const handleHomeClick = () => navigate('/');

  const handleApplyClick = async () => {
    if (!userId || !equipmentId) { alert('Нет userId или equipmentId'); return; }
    try {
      await axios.get(`/api/configuration/${userId}/${equipmentId}`);
      await axios.put(`/api/configuration/${userId}/${equipmentId}`, config);
    } catch (err) {
      if (err.response?.status === 404) {
        await axios.post(`/api/configuration/${userId}/${equipmentId}`, config);
      } else { console.error(err); alert('Ошибка сохранения'); return; }
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
          {initialBlocks.dataSources.map(b => <div key={b.id} className="block" draggable onDragStart={e => handleDragStartFromPanel(e,b)}>{b.label}</div>)}
          <h3>Функции</h3>
          {initialBlocks.functions.map(b => <div key={b.id} className="block" draggable onDragStart={e => handleDragStartFromPanel(e,b)}>{b.label}</div>)}
          <h3>Графики</h3>
          {initialBlocks.charts.map(b => <div key={b.id} className="block" draggable onDragStart={e => handleDragStartFromPanel(e,b)}>{b.label}</div>)}
        </aside>
        <section ref={canvasRef} className="canvas" onDrop={handleDrop} onDragOver={e => e.preventDefault()}>
          <svg className="connections">
            <defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7"/></marker></defs>
            {renderArrows()}
          </svg>
          {uiBlocks.map(b => <DraggableBlock key={b.uid} block={b} onDrag={handleBlockDrag} onStartConnection={startConnection} onCompleteConnection={completeConnection} onDelete={handleDeleteBlock}/>)}
        </section>
      </div>
    </div>
  );
};

export default Configurator;