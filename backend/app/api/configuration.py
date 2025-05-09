from flask import jsonify, Blueprint, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

from app import db
from app.core.block_processor import Block_Processor
from app.models.configuration import Configuration

configuration_bp = Blueprint('configuration', __name__)

# получить конфигурацию
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['GET'])
def get_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    return jsonify(config.to_dict()), 200

# добавление конфигурации
@configuration_bp.route('/<user_id>/<equipment_id>', methods=['POST'])
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
def delete_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404
    db.session.delete(config)
    db.session.commit()
    return jsonify({'message': 'Configuration deleted successfully'}), 200

@configuration_bp.route('/<user_id>/<equipment_id>/apply', methods=['GET'])
def apply_configuration(user_id, equipment_id):
    config = Configuration.query.get((user_id, equipment_id))
    if not config:
        return jsonify({'message': 'Нет конфигурация для этого пользователя и оборудования!'}), 404

    result = Block_Processor(config.config).process()
    #print(result)  # {'chart1': 10}
    return jsonify({'message': 'Configuration applied successfully', 'result': result}), 200