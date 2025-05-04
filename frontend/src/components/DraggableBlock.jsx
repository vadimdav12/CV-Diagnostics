import React, { useState, useRef } from 'react';

const DraggableBlock = ({ block, onDrag, onStartConnection, onCompleteConnection, onDelete }) => {
  const blockRef = useRef(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    const rect = blockRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e) => {
    onDrag(block.uid, e.movementX, e.movementY);
  };

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  // Обработчик правого клика для удаления блока
  const handleRightClick = (e) => {
    e.preventDefault(); // Отключаем стандартное контекстное меню
    onDelete(block.uid); // Вызываем функцию удаления
  };

  return (
    <div
      ref={blockRef}
      className={`canvas-block ${block.type}`}
      onMouseDown={handleMouseDown}
      onContextMenu={handleRightClick} // Добавляем обработчик правого клика
      style={{ left: block.x, top: block.y }}
    >
      {block.label}

      {/* Черная точка (output) */}
      <div
        className="output-dot"
        onClick={(e) => {
          e.stopPropagation();
          console.log("Start connection from", block.uid); // лог
          onStartConnection(block.uid);
        }}
      />

      {/* Зелёная точка (input) */}
      <div
        className="input-dot"
        onClick={(e) => {
          e.stopPropagation();
          console.log("Complete connection to", block.uid); // лог
          onCompleteConnection(block.uid);
        }}
      />
    </div>
  );
};

export default DraggableBlock;
