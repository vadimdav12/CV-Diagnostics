# app/api/sensors_parameters.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import event

from app import db, cache
from app.models.sensor import Sensor
from app.models.sensor_parameter import Sensor_parameter

sensors_parameters_bp = Blueprint('sensors_parameters', __name__, url_prefix='/api/sensors_parameters')

# Получить все параметры, назначенные датчику
@sensors_parameters_bp.route('/<int:sensor_id>', methods=['GET'])
@jwt_required()
def get_sensor_parameters(sensor_id):
    params = Sensor_parameter.query.filter_by(sensor_id=sensor_id).all()
    return jsonify([p.to_dict() for p in params]), 200

# Назначить параметр датчику
@sensors_parameters_bp.route('/<int:sensor_id>/<int:parameter_id>', methods=['POST'])
@jwt_required()
def add_sensor_parameter(sensor_id, parameter_id):
    data = request.get_json()

    if not data or not data.get('key'):
        return jsonify({'error': 'key param is required'}), 400

    # Проверяем на уникальность связки (sensor_id, parameter_id)
    if Sensor_parameter.query.filter_by(sensor_id=sensor_id, parameter_id=parameter_id).first():
        return jsonify({'message': 'Parameter already assigned'}), 400

    key = data.get('key')

    param = Sensor_parameter(sensor_id=sensor_id, parameter_id=parameter_id, key=key)
    db.session.add(param)
    db.session.commit()
    return jsonify(param.to_dict()), 201

# Удалить параметр у датчика
@sensors_parameters_bp.route('/<int:sensor_id>/<int:parameter_id>', methods=['DELETE'])
@jwt_required()
def delete_sensor_parameter(sensor_id, parameter_id):
    param = Sensor_parameter.query.filter_by(sensor_id=sensor_id, parameter_id=parameter_id).first()
    if not param:
        return jsonify({'message': 'Not found'}), 404

    db.session.delete(param)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200

#Необходимо для  MQTT !!!
# Функция для сброса кэша при изменениях Sensor_parameter
def clear_sensor_cache(mapper, connection, target):
    sensor = db.session.get(Sensor, target.sensor_id)
    if sensor:
        # Очищаем кэш для этого сенсора
        cache_key = f"sensor_params_{sensor.data_source}"
        cache.delete(cache_key)
        print(f"Cleared cache for {cache_key}")

# Регистрируем обработчики для всех значимых событий
event.listen(Sensor_parameter, 'after_insert', clear_sensor_cache)
event.listen(Sensor_parameter, 'after_update', clear_sensor_cache)
event.listen(Sensor_parameter, 'after_delete', clear_sensor_cache)