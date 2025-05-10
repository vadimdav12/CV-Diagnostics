# app/api/sensors_parameters.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.sensor_parameter import Sensor_parameter

sensors_parameters_bp = Blueprint('sensors_parameters', __name__, url_prefix='/api/sensors_parameters')

# Получить все параметры, назначенные датчику
@sensors_parameters_bp.route('/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_sensor_parameters(sensor_id):
    # Опционально: проверить user_id из токена, если параметры привязаны к пользователю
    params = Sensor_parameter.query.filter_by(sensor_id=sensor_id).all()
    return jsonify([p.to_dict() for p in params]), 200

# Назначить параметр датчику
@sensors_parameters_bp.route('/<int:sensor_id>/<int:parameter_id>', methods=['POST'])
@jwt_required()
def add_sensor_parameter(sensor_id, parameter_id):
    data = request.get_json()
    key = data.get('key')
    # Проверяем на уникальность связки (sensor_id, parameter_id)
    existing = Sensor_parameter.query.get((sensor_id, parameter_id))
    if existing:
        return jsonify({'message': 'Parameter already assigned'}), 400

    param = Sensor_parameter(
        sensor_id=sensor_id,
        parameter_id=parameter_id,
        key=key
    )
    db.session.add(param)
    db.session.commit()
    return jsonify(param.to_dict()), 201

# Удалить параметр у датчика
@sensors_parameters_bp.route('/<int:sensor_id>/<int:parameter_id>', methods=['DELETE'])
@jwt_required()
def delete_sensor_parameter(sensor_id, parameter_id):
    param = Sensor_parameter.query.get((sensor_id, parameter_id))
    if not param:
        return jsonify({'message': 'Not found'}), 404

    db.session.delete(param)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200
