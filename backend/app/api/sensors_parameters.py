from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

sensors_parameters_bp = Blueprint('sensors_parameters', __name__)

from ..models.sensor_parameter import Sensor_parameter
from app import db

@sensors_parameters_bp.route('/')
#@jwt_required()
def show_sensors_parameters():
    sensors_parameters = Sensor_parameter.query.all()

    return jsonify([{'id': sensors_parameters.id, 'key': sensors_parameters.key,
                     'sensor_id': sensors_parameters.sensor.name, 'parameter_id': sensors_parameters.parameter.name} for sensors_parameters in sensors_parameters])

# Добавление Sensor_parameter
@sensors_parameters_bp.route('/add', methods=['POST'])
def add_sensor():
    data = request.get_json()
    if not data or not data.get('key') or not data.get('sensor_id')\
            or not data.get('parameter_id'):
        return jsonify({'error': 'key, sensor_id and parameter_id are required'}), 400

    new_sensors_parameter = Sensor_parameter(key=data['key'], sensor_id=data['sensor_id'],parameter_id=data['parameter_id'])
    db.session.add(new_sensors_parameter)
    db.session.commit()
    return jsonify(new_sensors_parameter.to_dict()), 201


# Изменение sensors_parameters
@sensors_parameters_bp.route('/<sensors_parameters_id>', methods=['PUT'])
def update_sensor(sensors_parameters_id):
    sensors_parameters = Sensor_parameter.query.get_or_404(sensors_parameters_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'key' in data:
        sensors_parameters.key = data['key']
    if 'sensor_id' in data:
        sensors_parameters.sensor_id = data['sensor_id']
    if 'parameter_id' in data:
        sensors_parameters.parameter_id = data['parameter_id']
    db.session.commit()
    return jsonify(sensors_parameters.to_dict()), 200


# Удаление Sensor_parameter
@sensors_parameters_bp.route('/<sensors_parameters_id>', methods=['DELETE'])
def delete_sensor(sensors_parameters_id):
    sensors_parameters = Sensor_parameter.query.get_or_404(sensors_parameters_id)
    db.session.delete(sensors_parameters)
    db.session.commit()
    return jsonify({'message': 'Sensor_parameter deleted successfully'}), 200