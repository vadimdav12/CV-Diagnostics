import React, { useState, useRef } from 'react';

/**
 * Компонент перетаскиваемого блока для NoCode-конфигуратора
 * 
 * @param {Object} props - Входные параметры компонента
 * @param {Object} props.block - Данные блока (тип, позиция, параметры)
 * @param {Function} props.onDrag - Обработчик перемещения блока
 * @param {Function} props.onStartConnection - Обработчик начала создания соединения
 * @param {Function} props.onCompleteConnection - Обработчик завершения создания соединения
 * @param {Function} props.onDelete - Обработчик удаления блока
 */
const DraggableBlock = ({ block, onDrag, onStartConnection, onCompleteConnection, onDelete }) => {
  // Референс на DOM-элемент блока
  const blockRef = useRef(null);
  
  // Состояние для хранения смещения курсора при перетаскивании
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  /**
   * Обработчик нажатия кнопки мыши на блоке
   * @param {Object} e - Событие мыши
   */
  const handleMouseDown = (e) => {
    // Получаем размеры и позицию блока
    const rect = blockRef.current.getBoundingClientRect();
    
    // Запоминаем смещение курсора относительно верхнего левого угла блока
    setDragOffset({
      x: e.clientX - rect.left, // Горизонтальное смещение
      y: e.clientY - rect.top   // Вертикальное смещение
    });
    
    // Подписываемся на события перемещения и отпускания мыши
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  /**
   * Обработчик перемещения мыши при перетаскивании блока
   * @param {Object} e - Событие мыши
   */
  const handleMouseMove = (e) => {
    // Вызываем переданный обработчик с ID блока и смещениями
    onDrag(block.uid, e.movementX, e.movementY);
  };

  /**
   * Обработчик отпускания кнопки мыши
   * Отписывается от событий перемещения мыши
   */
  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  /**
   * Обработчик правого клика для удаления блока
   * @param {Object} e - Событие мыши
   */
  const handleRightClick = (e) => {
    e.preventDefault(); // Отменяем стандартное контекстное меню
    onDelete(block.uid); // Вызываем переданный обработчик удаления
  };

  return (
    <div
      ref={blockRef}
      className={`canvas-block ${block.type}`} // Классы для стилизации по типу блока
      onMouseDown={handleMouseDown} // Обработчик начала перетаскивания
      onContextMenu={handleRightClick} // Обработчик правого клика
      style={{ 
        left: block.x, // Позиция по X
        top: block.y   // Позиция по Y
      }}
    >
      {/* Заголовок блока с дополнительной информацией */}
      <div className="block-header">
        {block.label} {/* Основная метка блока */}
        
        {/* Дополнительная информация для датчиков */}
        {block.type === 'dataSource' && (
          <span className="block-details">ID: {block.parameters.sensor_id}</span>
        )}
      </div>

      {/* Точка для создания исходящего соединения (правая сторона) */}
      <div
        className="output-dot"
        title="Начать соединение (выход)"
        onClick={(e) => {
          e.stopPropagation(); // Предотвращаем всплытие события
          onStartConnection(block.uid); // Начинаем создание соединения
        }}
      />

      {/* Точка для создания входящего соединения (левая сторона) */}
      <div
        className="input-dot"
        title="Завершить соединение (вход)"
        onClick={(e) => {
          e.stopPropagation(); // Предотвращаем всплытие события
          onCompleteConnection(block.uid); // Завершаем создание соединения
        }}
      />
    </div>
  );
};

export default DraggableBlock;