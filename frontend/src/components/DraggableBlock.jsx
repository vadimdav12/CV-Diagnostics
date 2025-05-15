// frontend/src/components/DraggableBlock.jsx

import React, { useRef } from 'react';

/**
 * Перетаскиваемый блок с поддержкой drag-to-connect
 */
export default function DraggableBlock({
  block,
  onDrag,
  onDelete,
  onClick,
  onStartArrow
}) {
  const ref = useRef(null);

  // Начало перетаскивания блока
  const handleMouseDown = e => {
    e.stopPropagation();
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };
  const handleMouseMove = e => onDrag(block.uid, e.movementX, e.movementY);
  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  // Правый клик — удалить
  const handleContext = e => {
    e.preventDefault();
    onDelete(block.uid);
  };

  // Левый клик — выбрать
  const handleClick = e => {
    e.stopPropagation();
    onClick && onClick(block.uid);
  };

  // Начало рисования стрелки из правой точки
  const handleStart = e => {
    e.stopPropagation();
    onStartArrow(block.uid, e.clientX, e.clientY);
  };

  return (
    <div
      ref={ref}
      className={`canvas-block ${block.type}`}
      style={{ left: block.x, top: block.y }}
      onMouseDown={handleMouseDown}
      onContextMenu={handleContext}
      onClick={handleClick}
    >
      <div className="block-header">{block.label}</div>
      {/* точка выхода */}
      <div
        className="output-dot"
        title="Нажмите и тяните, чтобы соединить"
        onMouseDown={handleStart}
      />
      {/* точка входа */}
      <div className="input-dot" title="Точка входа" />
    </div>
  );
}
