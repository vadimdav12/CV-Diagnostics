from email.utils import parsedate_to_datetime

from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

sensor_records_bp = Blueprint('sensor_records', __name__)

from ..models.sensor_record import Sensor_Record

@sensor_records_bp.route('/')
#@jwt_required()
def show_all_sensor_records():
    sensor_records = Sensor_Record.query.all()

    return jsonify([{'id': sensor_record.id, 'timestamp': sensor_record.timestamp, 'value': sensor_record.value,
                     'sensor_id': sensor_record.sensor.name, 'parameter_id': sensor_record.parameter.name} for sensor_record in sensor_records])

@sensor_records_bp.route('/<sensor_id>')
#@jwt_required()
def show_sensor_records(sensor_id):
    sensor_records = Sensor_Record.query.filter_by(sensor_id=sensor_id)

    return jsonify([{'id': sensor_record.id, 'timestamp': sensor_record.timestamp, 'value': sensor_record.value,
                     'sensor_id': sensor_record.sensor.name, 'parameter_id': sensor_record.parameter.name} for sensor_record in sensor_records])


@sensor_records_bp.route('/raw_data/<sensor_id>')
#@jwt_required()
def show_sensor_records_raw_data(sensor_id):
    # Получаем параметры из URL
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    parameter = request.args.get('parameter')
    
    # Базовый запрос
    query = Sensor_Record.query
    # Фильтрация по дате
    if start_date:
        # try:
        #     start_date = datetime.strptime(start_date, '%Y-%m-%d')
        #     query = query.filter(Sensor_Record.timestamp >= start_date)
        # except ValueError:
        #     return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        try:
            # Конвертируем строку в datetime
            start_date = parsedate_to_datetime(start_date) if start_date else None
            query = query.filter(Sensor_Record.timestamp >= start_date)
        except (TypeError, ValueError):
            return {"error": "Invalid date format. Use 'MON, DD MM YYYY H:M:S GMT'"}, 400

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Sensor_Record.timestamp <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

    # Фильтрация по параметрам
    if parameter:
        query = query.filter(Sensor_Record.parameter == parameter)

    # Выполняем запрос
    results = query.order_by(Sensor_Record.timestamp.asc()).all()

    values = [result.value for result in query.with_entities(Sensor_Record.value).all()]

    return jsonify(values)
