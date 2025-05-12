from flask import jsonify, Blueprint, request
from flask_jwt_extended import  jwt_required

from app import db
from app.core.block_processor import Block_Processor
from app.models.configuration import Configuration

configuration_bp = Blueprint('configuration', __name__)

# получить конфигурацию
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['GET'])
@jwt_required()
def get_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    return jsonify(config.to_dict()), 200

# добавление конфигурации
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def delete_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    db.session.delete(config)
    db.session.commit()
    return jsonify({'message': 'Configuration deleted successfully'}), 200

@configuration_bp.route('/<user_id>/<equipment_id>/apply', methods=['GET'])
@jwt_required()
def apply_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурации для этого пользователя и оборудования!'}), 404

    raw_result = Block_Processor(config.config).process()
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
@jwt_required()
def get_functions():
    function_names = ['spectrum','func1']
    return jsonify({'result': function_names}), 200