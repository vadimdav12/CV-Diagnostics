from datetime import timedelta

from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

sensor_type_bp = Blueprint('sensor-type', __name__)

from ..models.sensor_type import Sensor_type
from app import db

@sensor_type_bp.route('/')
#@jwt_required()
def show_sensor_type():
    sensor_types = Sensor_type.query.all()

    return jsonify([{'id': sensor_type.id, 'name': sensor_type.name} for sensor_type in sensor_types])

# Добавление Sensor_type
@sensor_type_bp.route('/add', methods=['POST'])
def add_sensor():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'name and data_source are required'}), 400

    if Sensor_type.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Sensor_type already exists'}), 400

    new_sensor_type = Sensor_type(name=data['name'])
    db.session.add(new_sensor_type)
    db.session.commit()
    return jsonify(new_sensor_type.to_dict()), 201


# Изменение sensor_type
@sensor_type_bp.route('/<sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    sensor_type = Sensor_type.query.get_or_404(sensor_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        if data['name'] != sensor_type.name and Sensor_type.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'name already exists'}), 400
        sensor_type.name = data['name']

    db.session.commit()
    return jsonify(sensor_type.to_dict()), 200


# Удаление Sensor_type
@sensor_type_bp.route('/<sensor_type_id>', methods=['DELETE'])
def delete_sensor(sensor_type_id):
    sensor_type = Sensor_type.query.get_or_404(sensor_type_id)
    db.session.delete(sensor_type)
    db.session.commit()
    return jsonify({'message': 'Sensor_type deleted successfully'}), 200