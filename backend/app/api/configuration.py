from datetime import datetime

import pytz
from flask import jsonify, Blueprint, request
from flask_jwt_extended import  jwt_required

from app import db, cache
from app.core.block_processor import Block_Processor
from app.models.configuration import Configuration

configuration_bp = Blueprint('configuration', __name__)

# получить конфигурацию
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['GET'])
#@jwt_required()
def get_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    return jsonify(config.to_dict()), 200

# добавление конфигурации
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['POST'])
#@jwt_required()
def add_configuration(user_id, equipment_id):
    if not request.is_json:
        return jsonify({'message': 'Not JSON'}), 400

    try:
        data = request.json
    except:
        return jsonify({'message': 'Invalid JSON!'}), 400
    config = Configuration.query.get((user_id, equipment_id))
    if config:
        return jsonify({'message': 'Конфигурация для этого пользователя и оборудования уже есть!'}), 404
    config = Configuration(user_id=user_id, equipment_id=equipment_id, config=data)
    db.session.add(config)
    db.session.commit()
    return jsonify(config.to_dict()), 201

# Изменение конфигурации
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['PUT'])
#@jwt_required()
def update_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    try:
        data = request.json
    except:
        return jsonify({'message': 'Invalid JSON!'}), 400
    config.config = data
    db.session.commit()
    config = Configuration.query.get_or_404((user_id, equipment_id))
    return jsonify(config.to_dict()), 200


# Удаление конфигурации
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['DELETE'])
#@jwt_required()
def delete_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    db.session.delete(config)
    db.session.commit()
    return jsonify({'message': 'Configuration deleted successfully'}), 200

@configuration_bp.route('/<user_id>/<equipment_id>/apply', methods=['GET'])
#@jwt_required()
def apply_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурации для этого пользователя и оборудования!'}), 404

    # Получаем параметр `last_update` из запроса (в формате %Y-%m-%dT%H:%M:%S.%fZ)
    last_update_str = request.args.get('last_update')
    if not last_update_str:
        return jsonify({'message': 'Last_update arg needed'}), 401

    # Convert to Moscow time (UTC+3)
    last_update_str = '2024-12-12T00:00:00.461Z'
    timestamp_utc = datetime.strptime(last_update_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp_utc = pytz.utc.localize(timestamp_utc)
    moscow_tz = pytz.timezone('Europe/Moscow')
    timestamp = timestamp_utc.astimezone(moscow_tz)

    # Кэшируем данные
    # cache_key = f"prev_update_data_{user_id}_{equipment_id}"
    # cached = cache.get(cache_key)
    # if cached:
    #     import copy
    #     import numpy as np
    #
    #     prev_update = cached["prev_update"]
    #     prev_raw_result = cached["raw_result"]
    #     result = Block_Processor(config.config, prev_update).process()
    #     block_ids_to_delete = []
    #     print("prev-0",prev_raw_result)
    #     print("res-0",result)
    #     for block_id in prev_raw_result.keys():
    #         if block_id in result.keys():
    #             for values in prev_raw_result[block_id].keys():
    #                 # Объединяем два массива
    #                 prev_raw_result[block_id][values] = np.concatenate(
    #                     [prev_raw_result[block_id][values], result[block_id][values]])
    #         else:
    #             block_ids_to_delete.append(block_id)
    #     for key in result.keys():
    #         if not key in prev_raw_result.keys():
    #             prev_raw_result[key] = {}
    #     for block_id in block_ids_to_delete:
    #         # Очищаем кэш блока для этого сенсора
    #         print(prev_raw_result.pop(block_id, None))
    #
    #     raw_result = copy.deepcopy(prev_raw_result)
    #     print("prev-1", prev_raw_result)
    #     print("raw_result-1", raw_result)
    #
    #     # Обновляем значения из result
    #     # for key, value in result.items():
    #     #     if key in raw_result and isinstance(value, dict) and isinstance(raw_result[key], dict):
    #     #         raw_result[key].update(value)  # Обновляем вложенный словарь
    #     #     else:
    #     #         raw_result[key] = value
    # else:
    #     raw_result = Block_Processor(config.config).process()
    # cache.set(cache_key, {"prev_update": timestamp, 'raw_result':raw_result}, timeout=3600)

    raw_result = Block_Processor(config.config, timestamp).process()
    # Преобразуем numpy.ndarray в списки, чтобы JSON-сериализация прошла успешно
    serializable = {}
    for block_id, data in raw_result.items():
        x_vals = data.get('x_values', [])
        y_vals = data.get('y_values', [])
        serializable[block_id] = {
            'x_values': x_vals.tolist() if hasattr(x_vals, 'tolist') else list(x_vals),
            'y_values': y_vals.tolist() if hasattr(y_vals, 'tolist') else list(y_vals)
        }

    return jsonify({'message': 'Configuration applied successfully', 'result': serializable}), 200

@configuration_bp.route('/functions', methods=['GET'])
#@jwt_required()
def get_functions():
    function_names = ['spectrum','func1']
    return jsonify({'result': function_names}), 200