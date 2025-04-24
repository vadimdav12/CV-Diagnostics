from datetime import timedelta

from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

sensors_bp = Blueprint('sensors', __name__)

from ..models.sensor import Sensor
from app import db

@sensors_bp.route('/')
#@jwt_required()
def show_sensors():
    sensors = Sensor.query.all()

    return jsonify([{'id': sensor.id, 'name': sensor.name,'data_source': sensor.data_source,
                     'sensor_type_id': sensor.sensor_type.name, 'equipment': sensor.equipment.name} for sensor in sensors])

# Добавление sensor
@sensors_bp.route('/add', methods=['POST'])
def add_sensor():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('data_source') or not data.get('sensor_type_id')\
            or not data.get('equipment_id'):
        return jsonify({'error': 'name and data_source are required'}), 400

    if Sensor.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Sensor already exists'}), 400

    new_sensor = Sensor(name=data['name'], data_source=data['data_source'], sensor_type_id=data['sensor_type_id'],
                        equipment_id=data['equipment_id'])
    db.session.add(new_sensor)
    db.session.commit()
    return jsonify(new_sensor.to_dict()), 201


# Изменение sensor
@sensors_bp.route('/<sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        if data['name'] != sensor.name and Sensor.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'name already exists'}), 400
        sensor.name = data['name']
    sensor.data_source = data['data_source']
    sensor.sensor_type_id = data['sensor_type_id']
    sensor.equipment_id = data['equipment_id']

    db.session.commit()
    return jsonify(sensor.to_dict()), 200


# Удаление sensor
@sensors_bp.route('/<sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    db.session.delete(sensor)
    db.session.commit()
    return jsonify({'message': 'Sensor deleted successfully'}), 200