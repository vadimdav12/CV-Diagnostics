# Основная логика
import json
from typing import Dict, Any, List, Optional
from app.algorithms.algorithms import execute_function


class Block_Processor:
    def __init__(self, config: Dict[str, Any], last_update=-1):
        self.config = config
        self.blocks = config.get('blocks', {})
        self.connections = config.get('connections', [])
        self.values_y: Dict[str, Any] = {}  # Хранит вычисленные значения блоков по X
        self.values_x: Dict[str, Any] = {}  # Хранит вычисленные значения блоков по Y
        self.last_update = last_update

    def process(self):
        # 1. Найти все блоки-источники (тип 'dataSource')
        sources = [block_id for block_id, block in self.blocks.items()
                   if block.get('type') == 'dataSource']

        # 2. Для каждого источника запускаем распространение данных
        for source_id in sources:
            self._compute_data(source_id)
        # 3. Возвращаем только значения графиков (тип 'chart')
        return {block_id: {'x_values': self.values_x.get(block_id), 'y_values': self.values_y.get(block_id)}
                for block_id, block in self.blocks.items()
                if block.get('type') == 'chart'}

    def _compute_data(self, block_id: str):
        """Рекурсивно распространяет данные от блока к следующим блокам"""
        # Получаем текущее значение блока (если еще не вычислено)
        if block_id not in self.values_y:
            self.values_x[block_id], self.values_y[block_id] = self._compute_block_value(block_id)

        # Находим все соединения, где текущий блок является источником
        outgoing_conns = [conn for conn in self.connections
                          if conn['source'] == block_id]

        # Передаем данные следующим блокам
        for conn in outgoing_conns:
            target_id = conn['target']
            if target_id not in self.values_y:  # Избегаем циклов
                self._compute_data(target_id)

    def _compute_block_value(self, block_id: str) -> Any:
        """Вычисляет значение блока на основе его типа и входных данных"""
        block = self.blocks[block_id]

        if block['type'] == 'dataSource':
            sensor_id = block['parameters'].get('sensor_id')
            parameter_id = block['parameters'].get('parameter_id')
            if self.last_update == -1:
                timestamps, values = get_data(sensor_id, parameter_id)
            else:
                timestamps, values = get_data(sensor_id, parameter_id, self.last_update)
            return timestamps, values

        elif block['type'] == 'function':
            # Функция - получаем входные данные и применяем
            input_value_x,  input_value_y= self._get_input_value(block_id)
            function = block['parameters'].get('function')
            return execute_function(function, input_value_x, input_value_y)

        elif block['type'] == 'chart':
            # График - просто возвращаем входные данные
            return self._get_input_value(block_id)

        return None

    def _get_input_value(self, block_id: str) -> Any:
        """Получает входное значение для блока из соединений"""
        incoming_conns = [conn for conn in self.connections
                          if conn['target'] == block_id]

        if not incoming_conns:
            return None

        #  берем первое входящее соединение
        source_id = incoming_conns[0]['source']
        return self.values_x.get(source_id), self.values_y.get(source_id)

def get_data(sensor_id, parameter_id, last_update=-1):
    from ..models.sensor_record import Sensor_Record
    from app import db

    # Источник данных - берем значение из параметров
    if last_update == -1:
        result = db.session.execute(db.select(Sensor_Record.value, Sensor_Record.timestamp)
            .filter_by(sensor_id=sensor_id, parameter_id=parameter_id).order_by(Sensor_Record.timestamp)).all()
    else:
        # Запрос только новых данных, которые появились после `last_update`
        result = Sensor_Record.query.with_entities(Sensor_Record.sensor_id, Sensor_Record.parameter_id,
            Sensor_Record.timestamp, Sensor_Record.value).filter(Sensor_Record.sensor_id==sensor_id,
            Sensor_Record.parameter_id==parameter_id, Sensor_Record.timestamp > last_update
        ).order_by(Sensor_Record.timestamp).all()

    values = [row.value for row in result]
    timestamps = [row.timestamp for row in result]
    return timestamps, values