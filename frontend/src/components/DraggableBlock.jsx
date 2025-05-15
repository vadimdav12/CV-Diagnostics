// frontend/src/components/DraggableBlock.jsx

import React, { useState, useRef } from 'react';

/**
 * Компонент перетаскиваемого блока для NoCode-конфигуратора
 */
const DraggableBlock = ({
  block,
  onDrag,
  onStartConnection,
  onCompleteConnection,
  onDelete,
  onClick
}) => {
  const blockRef = useRef(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    const rect = blockRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
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

  const handleRightClick = (e) => {
    e.preventDefault();
    onDelete(block.uid);
  };

  const handleClick = (e) => {
    e.stopPropagation();
    if (onClick) onClick(block.uid);
  };

  return (
    <div
      ref={blockRef}
      className={`canvas-block ${block.type}`}
      style={{ left: block.x, top: block.y }}
      onMouseDown={handleMouseDown}
      onContextMenu={handleRightClick}
      onClick={handleClick}
    >
      <div className="block-header">
        {block.label}
        {block.type === 'dataSource' && (
          <span className="block-details">ID: {block.parameters.sensor_id}</span>
        )}
      </div>
      <div
        className="output-dot"
        title="Начать соединение (выход)"
        onClick={(e) => {
          e.stopPropagation();
          onStartConnection(block.uid);
        }}
      />
      <div
        className="input-dot"
        title="Завершить соединение (вход)"
        onClick={(e) => {
          e.stopPropagation();
          onCompleteConnection(block.uid);
        }}
      />
    </div>
  );
};

export default DraggableBlock;
