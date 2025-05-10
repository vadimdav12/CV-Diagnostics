from email.utils import parsedate_to_datetime

from flask import jsonify, make_response, request, abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

sensor_records_bp = Blueprint('sensor_records', __name__)

from ..models.sensor_record import Sensor_Record


@sensor_records_bp.route('/')
# @jwt_required()
def show_all_sensor_records():
    sensor_records = Sensor_Record.query.all()

    return jsonify([{'id': sensor_record.id, 'timestamp': sensor_record.timestamp, 'value': sensor_record.value,
                     'sensor_id': sensor_record.sensor.name, 'parameter_id': sensor_record.parameter.name} for
                    sensor_record in sensor_records])


@sensor_records_bp.route('/<sensor_id>')
# @jwt_required()
def show_sensor_records(sensor_id):
    sensor_record = Sensor_Record.query.filter_by(sensor_id=sensor_id).first()

    if not sensor_record:
        return jsonify({'error': 'Sensor record doesn\'t  exist'}), 400

    query = Sensor_Record.query.filter_by(sensor_id=sensor_id)
    parameter_ids = [result.parameter_id for result in query.with_entities(Sensor_Record.parameter_id).distinct().all()]
    params_values = []
    for id in parameter_ids:
        values = [result.value for result in
                  query.filter(Sensor_Record.parameter_id == id, Sensor_Record.sensor_id == sensor_id).with_entities(Sensor_Record.value).all()]
        params_values.append({'parameter_id': id, 'values': values})

    result = jsonify({'sensor_id': sensor_id, 'values': params_values})
    return result
    # return jsonify([{'id': sensor_record.id, 'timestamp': sensor_record.timestamp, 'value': sensor_record.value,
    #                  'sensor_id': sensor_record.sensor.name, 'parameter_id': sensor_record.parameter.name} for sensor_record in sensor_records])


@sensor_records_bp.route('/raw_data/<sensor_id>')
# @jwt_required()
def show_sensor_records_raw_data(sensor_id):
    # Получаем параметры из URL
    start_datetime_str = request.args.get('start_date')
    end_datetime_str = request.args.get('end_date')
    parameter = request.args.get('parameter')

    # Базовый запрос
    query = Sensor_Record.query.filter(Sensor_Record.sensor_id == sensor_id)
    # Фильтрация по дате и времени
    if start_datetime_str:
        try:
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
            query = query.filter(Sensor_Record.timestamp >= start_datetime)
        except ValueError:
            return jsonify({"error": "Неверный формат start_datetime. Используйте DD.MM.YYYY HH:MM:SS"}), 400

    if end_datetime_str:
        try:
            # end_datetime = datetime.strptime(end_datetime_str, '%d.%m.%Y %H:%M:%S')
            end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
            query = query.filter(Sensor_Record.timestamp <= end_datetime)
        except ValueError:
            return jsonify({"error": "Неверный формат end_datetime. Используйте DD.MM.YYYY HH:MM:SS"}), 400

    # Фильтрация по параметрам
    if parameter:
        query = query.filter(Sensor_Record.parameter_id == parameter)

    # Выполняем запрос
    values = [result.value for result in query.with_entities(Sensor_Record.value).all()]

    return jsonify(values)
