from datetime import timedelta

from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

equipment_bp = Blueprint('equipment', __name__)

from ..models.equipment import Equipment, Equipment
from app import db

@equipment_bp.route('/')
#@jwt_required()
def show_equipment():
    equipments = Equipment.query.all()

    return jsonify([{'id': equipment.id, 'name': equipment.name} for equipment in equipments])

# Добавление equipment
@equipment_bp.route('/add', methods=['POST'])
def add_equipment():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'name  required'}), 400

    if Equipment.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Equipment already exists'}), 400

    new_equipment = Equipment(name=data['name'])
    db.session.add(new_equipment)
    db.session.commit()
    return jsonify(new_equipment.to_dict()), 201


# Изменение equipment
@equipment_bp.route('/<equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        if data['name'] != equipment.name and Equipment.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'name already exists'}), 400
        equipment.name = data['name']

    db.session.commit()
    return jsonify(equipment.to_dict()), 200


# Удаление equipment
@equipment_bp.route('/<equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)

    if equipment.sensors:
        return jsonify({"error": "Cannot delete equipment: it is referenced by one or more sensors"}), 400

    db.session.delete(equipment)
    db.session.commit()
    return jsonify({'message': 'Equipment deleted successfully'}), 200