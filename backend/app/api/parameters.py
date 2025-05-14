from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

parameter_bp = Blueprint('parameter', __name__)

from ..models.parameter import Parameter
from app import db

@parameter_bp.route('/', methods=['GET'])
#@jwt_required()
def show_parameter():
    parameters = Parameter.query.all()

    return jsonify([{'id': parameter.id, 'name': parameter.name, 'unit': parameter.unit} for parameter in parameters])

# Добавление Parameter
@parameter_bp.route('/add', methods=['POST'])
#@jwt_required()
def add_sensor():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('unit'):
        return jsonify({'error': 'name and unit are required'}), 400

    if Parameter.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Parameter already exists'}), 400

    new_parameter = Parameter(name=data['name'], unit=data['unit'])
    db.session.add(new_parameter)
    db.session.commit()
    return jsonify(new_parameter.to_dict()), 201


# Изменение parameter
@parameter_bp.route('/<parameter_id>', methods=['PUT'])
#@jwt_required()
def update_sensor(parameter_id):
    parameter = Parameter.query.get_or_404(parameter_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        if data['name'] != parameter.name and Parameter.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'name already exists'}), 400
        parameter.name = data['name']
        if 'unit' in data:
            parameter.unit = data['unit']

    db.session.commit()
    return jsonify(parameter.to_dict()), 200


# Удаление Parameter
@parameter_bp.route('/<parameter_id>', methods=['DELETE'])
#@jwt_required()
def delete_sensor(parameter_id):
    parameter = Parameter.query.get_or_404(parameter_id)

    if parameter.sensor_parameter or parameter.parameter_record:
        return jsonify({"error": "Cannot delete parameter: it is referenced by one or more sensor or sensor record"}), 400

    db.session.delete(parameter)
    db.session.commit()
    return jsonify({'message': 'Parameter deleted successfully'}), 200