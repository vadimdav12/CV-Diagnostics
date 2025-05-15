# backend/app/core/block_processor.py

import json
from typing import Dict, Any, List, Optional
from app.algorithms.algorithms import execute_function
from ..models.sensor_record import Sensor_Record
from app import db

class Block_Processor:
    def __init__(self, config: Dict[str, Any], last_update: Any = -1):
        self.config = config
        self.blocks = config.get('blocks', {})
        self.connections = config.get('connections', [])
        self.values_y: Dict[str, Any] = {}
        self.values_x: Dict[str, Any] = {}
        self.last_update = last_update

    def process(self) -> Dict[str, Dict[str, List[Any]]]:
        # Только источники с выбранным parameter_id
        sources = [
            block_id for block_id, block in self.blocks.items()
            if block.get('type') == 'dataSource'
            and block.get('parameters', {}).get('parameter_id')
        ]

        for source_id in sources:
            self._compute_data(source_id)

        # Возвращаем только графики
        return {
            block_id: {
                'x_values': self.values_x.get(block_id, []),
                'y_values': self.values_y.get(block_id, [])
            }
            for block_id, block in self.blocks.items()
            if block.get('type') == 'chart'
        }

    def _compute_data(self, block_id: str):
        if block_id not in self.values_y:
            self.values_x[block_id], self.values_y[block_id] = self._compute_block_value(block_id)

        outgoing = [c for c in self.connections if c['source'] == block_id]
        for conn in outgoing:
            tgt = conn['target']
            if tgt not in self.values_y:
                self._compute_data(tgt)

    def _compute_block_value(self, block_id: str) -> Any:
        block = self.blocks[block_id]

        if block['type'] == 'dataSource':
            sensor_id    = block['parameters'].get('sensor_id')
            parameter_id = block['parameters'].get('parameter_id')

            # Если нет сенсора или параметра — возвращаем пустые списки
            if not sensor_id or not parameter_id:
                return [], []

            # Приводим к int, безопасно
            try:
                sid = int(sensor_id)
                pid = int(parameter_id)
            except (TypeError, ValueError):
                return [], []

            if self.last_update == -1:
                return get_data(sid, pid)
            return get_data(sid, pid, self.last_update)

        elif block['type'] == 'function':
            x_in, y_in = self._get_input_value(block_id)
            func_name = block['parameters'].get('function')
            return execute_function(func_name, x_in, y_in)

        elif block['type'] == 'chart':
            return self._get_input_value(block_id)

        # По умолчанию — пусто
        return [], []

    def _get_input_value(self, block_id: str) -> Any:
        incoming = [c for c in self.connections if c['target'] == block_id]
        if not incoming:
            return [], []
        src = incoming[0]['source']
        return self.values_x.get(src, []), self.values_y.get(src, [])

def get_data(sensor_id: int, parameter_id: int, last_update: Any = -1):
    """
    Возвращает timestamp и value из sensor_records.
    Если last_update != -1, возвращаем только новые записи.
    """
    if last_update == -1:
        rows = db.session.execute(
            db.select(Sensor_Record.timestamp, Sensor_Record.value)
              .filter_by(sensor_id=sensor_id, parameter_id=parameter_id)
              .order_by(Sensor_Record.timestamp)
        ).all()
    else:
        rows = Sensor_Record.query \
            .with_entities(Sensor_Record.timestamp, Sensor_Record.value) \
            .filter(
                Sensor_Record.sensor_id == sensor_id,
                Sensor_Record.parameter_id == parameter_id,
                Sensor_Record.timestamp > last_update
            ) \
            .order_by(Sensor_Record.timestamp) \
            .all()

    timestamps = [r.timestamp for r in rows]
    values     = [float(r.value) for r in rows]
    return timestamps, values
