import React, { useState, useRef } from 'react';
import DraggableBlock from '../components/DraggableBlock.jsx';
import '../components/configurator.css';

const initialBlocks = {
  sensors: [
    { id: 'sensor1', label: 'Тепловой датчик', type: 'sensor' },
    { id: 'sensor2', label: 'Вибро датчик', type: 'sensor' },
    { id: 'sensor3', label: 'Токовый датчик', type: 'sensor' }
  ],
  functions: [
    { id: 'func1', label: 'Преобразование Фурье', type: 'function' },
    { id: 'func2', label: 'Фильтр', type: 'function' }
  ],
  graphs: [
    { id: 'graph1', label: 'Временной график', type: 'graph' },
    { id: 'graph2', label: 'Частотный график', type: 'graph' }
  ]
};

const Configurator = () => {
  const [canvasBlocks, setCanvasBlocks] = useState([]);
  const [connections, setConnections] = useState([]);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const canvasRef = useRef(null);

  const handleDrop = (e) => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;

    const block = JSON.parse(data);
    const rect = canvasRef.current.getBoundingClientRect();
    const newBlock = {
      ...block,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      uid: `${block.id}-${Date.now()}`
    };
    setCanvasBlocks([...canvasBlocks, newBlock]);
  };

  const handleDragStartFromPanel = (e, block) => {
    e.dataTransfer.setData('block', JSON.stringify(block));
  };

  const startConnection = (fromId) => {
    setConnectingFrom(fromId);
  };

  const completeConnection = (toId) => {
    if (!connectingFrom || connectingFrom === toId) return;

    const fromBlock = canvasBlocks.find(b => b.uid === connectingFrom);
    const toBlock = canvasBlocks.find(b => b.uid === toId);

    if (!fromBlock || !toBlock) return;

    const isValidConnection =
      (fromBlock.type === 'sensor' && toBlock.type === 'function') ||
      (fromBlock.type === 'function' && toBlock.type === 'graph');

    if (isValidConnection) {
      setConnections(prev => [...prev, { from: connectingFrom, to: toId }]);
    } else {
      alert('Неверное соединение: разрешено только "sensor → function" или "function → graph"');
    }

    setConnectingFrom(null);
  };

  const renderArrows = () => {
    console.log("Rendering arrows:", connections);

    return connections.map(({ from, to }, i) => {
      const fromBlock = canvasBlocks.find(b => b.uid === from);
      const toBlock = canvasBlocks.find(b => b.uid === to);

      if (!fromBlock || !toBlock) return null;

      const startX = fromBlock.x + 140;
      const startY = fromBlock.y + 25;
      const endX = toBlock.x;
      const endY = toBlock.y + 25;

      return (
        <line
          key={i}
          x1={startX}
          y1={startY}
          x2={endX}
          y2={endY}
          stroke="black"
          strokeWidth={2}
          markerEnd="url(#arrowhead)"
        />
      );
    });
  };

  const handleBlockDrag = (uid, dx, dy) => {
    setCanvasBlocks(prev =>
      prev.map(b => b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b)
    );
  };

  // Функция для удаления блока
  const handleDeleteBlock = (uid) => {
    setCanvasBlocks(prev => prev.filter(block => block.uid !== uid));
  };

  const handleHomeClick = () => {
    // Логика для перехода на главную страницу
    console.log("Переход на главную");
  };

  const handleApplyClick = () => {
    // Логика для применения изменений
    console.log("Изменения применены");
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
          {initialBlocks.sensors.map(block => (
            <div
              key={block.id}
              className="block"
              draggable
              onDragStart={(e) => handleDragStartFromPanel(e, block)}
            >
              {block.label}
            </div>
          ))}

          <h3>Функции</h3>
          {initialBlocks.functions.map(block => (
            <div
              key={block.id}
              className="block"
              draggable
              onDragStart={(e) => handleDragStartFromPanel(e, block)}
            >
              {block.label}
            </div>
          ))}

          <h3>Графики</h3>
          {initialBlocks.graphs.map(block => (
            <div
              key={block.id}
              className="block"
              draggable
              onDragStart={(e) => handleDragStartFromPanel(e, block)}
            >
              {block.label}
            </div>
          ))}
        </aside>

        <section
          ref={canvasRef}
          className="canvas"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <svg
            className="connections"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              pointerEvents: 'none',
              zIndex: 0
            }}
          >
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="10"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="black" />
              </marker>
            </defs>
            {renderArrows()}
          </svg>

          {canvasBlocks.map(block => (
            <DraggableBlock
              key={block.uid}
              block={block}
              onDrag={handleBlockDrag}
              onStartConnection={startConnection}
              onCompleteConnection={completeConnection}
              onDelete={handleDeleteBlock}  // Передаем handleDeleteBlock
            />
          ))}
        </section>
      </div>
    </div>
  );
};

export default Configurator;
