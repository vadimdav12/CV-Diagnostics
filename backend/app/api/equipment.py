from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from app import db
from ..models.equipment import Equipment
from ..models.sensor import Sensor
from ..models.sensor_type import Sensor_type
from ..models.parameter import Parameter
from ..models.sensor_parameter import Sensor_parameter

equipment_bp = Blueprint('equipment', __name__, url_prefix='/api/equipment')

# 1) Список оборудования
@equipment_bp.route('/', methods=['GET'])
@jwt_required()
@cross_origin(origins="http://localhost:3000", methods=["GET"])
def show_equipment():
    eqs = Equipment.query.all()
    return jsonify([e.to_dict() for e in eqs]), 200

# 2) Добавление оборудования
@equipment_bp.route('/add', methods=['OPTIONS','POST'])
@jwt_required()
@cross_origin(origins="http://localhost:3000", methods=["OPTIONS","POST"])
def add_equipment():
    # предзапрос
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'name required'}), 400

    if Equipment.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'already exists'}), 400

    new = Equipment(name=data['name'])
    db.session.add(new)
    db.session.commit()
    return jsonify(new.to_dict()), 201

# 3) Вложенный эндпоинт: добавить датчик к оборудованию
@equipment_bp.route('/<int:equipment_id>/sensors', methods=['OPTIONS','POST'])
@jwt_required()
@cross_origin(origins="http://localhost:3000", methods=["OPTIONS","POST"])
def add_sensor_to_equipment(equipment_id):
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    # проверка обязательных полей
    required = ['name','data_source','sensor_type_id']
    if not data or any(not data.get(f) for f in required):
        return jsonify({'error': f'Fields {required} required'}), 400

    # создаём датчик
    sensor = Sensor(
        name=data['name'],
        data_source=data['data_source'],
        sensor_type_id=data['sensor_type_id'],
        equipment_id=equipment_id
    )
    db.session.add(sensor)
    db.session.commit()

    # если нужны параметры — можно сразу связать, например:
    # params = data.get('parameters', [])
    # for pid in params:
    #     sp = Sensor_parameter(sensor_id=sensor.id, parameter_id=pid)
    #     db.session.add(sp)
    # db.session.commit()

    return jsonify(sensor.to_dict()), 201

# 4) Обновление и удаление оборудования (аналогично)
@equipment_bp.route('/<int:equipment_id>', methods=['PUT','DELETE','OPTIONS'])
@jwt_required()
@cross_origin(origins="http://localhost:3000", methods=["OPTIONS","PUT","DELETE"])
def modify_equipment(equipment_id):
    if request.method == 'OPTIONS':
        return '', 200

    eq = Equipment.query.get_or_404(equipment_id)
    if request.method == 'DELETE':
        db.session.delete(eq)
        db.session.commit()
        return jsonify({'message': 'deleted'}), 200

    # PUT
    data = request.get_json()
    if data.get('name'):
        eq.name = data['name']
    db.session.commit()
    return jsonify(eq.to_dict()), 200
