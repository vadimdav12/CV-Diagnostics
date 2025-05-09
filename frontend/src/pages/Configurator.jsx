import React, { useState, useRef } from 'react';
import DraggableBlock from '../components/DraggableBlock.jsx';
import '../components/configurator.css';

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
    { id: 'func1', label: 'Фурье', type: 'function', parameters: { function: 'fourier' } },
    { id: 'func2', label: 'Фильтр', type: 'function', parameters: { function: 'filter' } }
  ],
  charts: [
    { id: 'chart1', label: 'Временной график', type: 'chart', parameters: { chart_type: 'time' } },
    { id: 'chart2', label: 'Частотный график', type: 'chart', parameters: { chart_type: 'frequency' } }
  ]
};

/**
 * Основной компонент NoCode-конфигуратора
 * Управляет состоянием приложения, обработкой событий и отображением интерфейса
 */
const Configurator = () => {
  // Состояние конфигурации (блоки и соединения)
  const [config, setConfig] = useState({
    version: "1.0",
    blocks: {},
    connections: []
  });

  // Состояние UI-блоков (для отображения на холсте)
  const [uiBlocks, setUiBlocks] = useState([]);
  
  // ID блока, от которого начинается соединение
  const [connectingFrom, setConnectingFrom] = useState(null);
  
  // Референс на холст
  const canvasRef = useRef(null);

  /**
   * Обработчик события drop (перетаскивание блоков на холст)
   * @param {Object} e - Событие перетаскивания
   */
  const handleDrop = (e) => {
    const data = e.dataTransfer.getData('block');
    if (!data) return;

    const block = JSON.parse(data);
    const rect = canvasRef.current.getBoundingClientRect();
    
    // Генерация уникального ID для нового блока
    const blockId = `${block.type}_${Date.now()}`;
    
    // Создание нового блока с координатами
    const newBlock = {
      ...block,
      x: e.clientX - rect.left, // Позиция X относительно холста
      y: e.clientY - rect.top,  // Позиция Y относительно холста
      uid: blockId              // Уникальный идентификатор
    };

    // Добавление блока в UI и конфигурацию
    setUiBlocks([...uiBlocks, newBlock]);
    setConfig(prev => ({
      ...prev,
      blocks: {
        ...prev.blocks,
        [blockId]: {
          type: block.type,
          parameters: block.parameters
        }
      }
    }));
  };

  /**
   * Обработчик начала перетаскивания блока из панели
   * @param {Object} e - Событие перетаскивания
   * @param {Object} block - Данные блока
   */
  const handleDragStartFromPanel = (e, block) => {
    e.dataTransfer.setData('block', JSON.stringify(block));
  };

  /**
   * Начало создания соединения (клик на output-dot)
   * @param {string} fromId - ID блока-источника
   */
  const startConnection = (fromId) => {
    setConnectingFrom(fromId);
  };

  /**
   * Завершение создания соединения (клик на input-dot)
   * Выполняет проверки перед созданием соединения:
   * - Проверка типов блоков
   * - Проверка на отсутствие множественных соединений
   * @param {string} toId - ID блока-приемника
   */
  const completeConnection = (toId) => {
    if (!connectingFrom || connectingFrom === toId) return;
  
    const fromBlock = uiBlocks.find(b => b.uid === connectingFrom);
    const toBlock = uiBlocks.find(b => b.uid === toId);
  
    if (!fromBlock || !toBlock) return;
  
    // Проверка допустимости соединения по типам
    const isValidTypeConnection = (fromType, toType) => {
      const rules = {
        dataSource: ["function"], // Датчик можно соединить только с функцией
        function: ["chart"],     // Функцию можно соединить только с графиком
        chart: []                // График нельзя ни с чем соединять
      };
      return rules[fromType]?.includes(toType);
    };
  
    // Проверка что у источника нет других исходящих соединений
    const hasSourceOutgoingConnections = config.connections.some(
      conn => conn.source === connectingFrom
    );
  
    // Проверка что у приемника нет других входящих соединений
    const hasTargetIncomingConnections = config.connections.some(
      conn => conn.target === toId
    );
  
    if (!isValidTypeConnection(fromBlock.type, toBlock.type)) {
      alert('Неверное соединение: разрешено только "dataSource → function" или "function → chart"');
    } else if (hasSourceOutgoingConnections) {
      alert('Источник уже имеет исходящее соединение! Разрешено только одно исходящее соединение.');
    } else if (hasTargetIncomingConnections) {
      alert('Приемник уже имеет входящее соединение! Разрешено только одно входящее соединение.');
    } else {
      // Добавление нового соединения в конфигурацию
      setConfig(prev => ({
        ...prev,
        connections: [...prev.connections, { source: connectingFrom, target: toId }]
      }));
    }
  
    setConnectingFrom(null);
  };

  /**
   * Отрисовка стрелок соединений между блоками
   * @returns {Array} Массив SVG-элементов <line>
   */
  const renderArrows = () => {
    return config.connections.map(({ source, target }, i) => {
      const fromBlock = uiBlocks.find(b => b.uid === source);
      const toBlock = uiBlocks.find(b => b.uid === target);
  
      if (!fromBlock || !toBlock) return null;
  
      // Координаты центра output-dot (правый кружок)
      const startX = fromBlock.x + 160; // Ширина блока (160px) + позиция X
      const startY = fromBlock.y + 30;  // Центр по вертикали (высота блока ~60px)
  
      // Координаты центра input-dot (левый кружок)
      const endX = toBlock.x;
      const endY = toBlock.y + 30;
  
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

  /**
   * Обработчик перемещения блока на холсте
   * @param {string} uid - ID блока
   * @param {number} dx - Изменение по X
   * @param {number} dy - Изменение по Y
   */
  const handleBlockDrag = (uid, dx, dy) => {
    setUiBlocks(prev =>
      prev.map(b => b.uid === uid ? { ...b, x: b.x + dx, y: b.y + dy } : b)
    );
  };

  /**
   * Удаление блока и связанных с ним соединений
   * @param {string} uid - ID блока для удаления
   */
  const handleDeleteBlock = (uid) => {
    setUiBlocks(prev => prev.filter(block => block.uid !== uid));
    setConfig(prev => ({
      ...prev,
      blocks: Object.fromEntries(Object.entries(prev.blocks).filter(([id]) => id !== uid)),
      connections: prev.connections.filter(conn => conn.source !== uid && conn.target !== uid)
    }));
  };

  /**
   * Обработчик клика по кнопке "Домой"
   */
  const handleHomeClick = () => {
    console.log("Переход на главную");
  };

  /**
   * Обработчик клика по кнопке "Применить изменения"
   * Отправляет текущую конфигурацию на сервер
   */
  const handleApplyClick = async () => {
    try {
      console.log("Отправка конфигурации:", config);
      // Здесь будет вызов API для сохранения конфигурации
      // const response = await fetch('/api/save-config', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(config)
      // });
      alert(`Конфигурация готова к отправке:\n${JSON.stringify(config, null, 2)}`);
    } catch (error) {
      console.error("Ошибка:", error);
    }
  };

  return (
    <div className="configurator">
      {/* Верхняя панель с заголовком и кнопками */}
      <header className="top-bar">
        <div className="header-content">
          <span>No-code конфигуратор</span>
          <div className="header-buttons">
            <button onClick={handleHomeClick}>Домой</button>
            <button onClick={handleApplyClick}>Применить изменения</button>
          </div>
        </div>
      </header>

      {/* Основная область (панель инструментов + холст) */}
      <div className="main">
        {/* Боковая панель с блоками */}
        <aside className="sidebar">
          <h3>Датчики</h3>
          {initialBlocks.dataSources.map(block => (
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
          {initialBlocks.charts.map(block => (
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

        {/* Холст для размещения блоков */}
        <section
          ref={canvasRef}
          className="canvas"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {/* SVG-слой для отрисовки соединений */}
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

          {/* Отображение блоков на холсте */}
          {uiBlocks.map(block => (
            <DraggableBlock
              key={block.uid}
              block={block}
              onDrag={handleBlockDrag}
              onStartConnection={startConnection}
              onCompleteConnection={completeConnection}
              onDelete={handleDeleteBlock}
            />
          ))}
        </section>
      </div>
    </div>
  );
};

export default Configurator;