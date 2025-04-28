import pytest
from flask import url_for, json
from datetime import datetime, timedelta
from email.utils import formatdate
from backend.app.models.sensor_record import Sensor_Record
from backend.app.models.sensor import Sensor
from backend.app.models.parameter import Parameter

# =====================
# POSITIVE TESTS
# =====================

def test_show_all_sensor_records(client, init_database):
    """Тест получения всех записей сенсоров"""
    # Создаем тестовые данные
    sensor = Sensor(name="Test Sensor")
    param = Parameter(name="Temperature", unit="C")
    db.session.add(sensor)
    db.session.add(param)
    
    record1 = Sensor_Record(
        timestamp=datetime.utcnow(),
        value=25.5,
        sensor=sensor,
        parameter=param
    )
    record2 = Sensor_Record(
        timestamp=datetime.utcnow() - timedelta(hours=1),
        value=26.0,
        sensor=sensor,
        parameter=param
    )
    db.session.add(record1)
    db.session.add(record2)
    db.session.commit()

    response = client.get(url_for('sensor_records.show_all_sensor_records'))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['value'] == 25.5
    assert data[1]['value'] == 26.0

def test_show_sensor_records(client, init_database):
    """Тест получения записей конкретного сенсора"""
    sensor1 = Sensor(name="Sensor 1")
    sensor2 = Sensor(name="Sensor 2")
    param = Parameter(name="Temperature", unit="C")
    db.session.add_all([sensor1, sensor2, param])
    
    # Добавляем записи для sensor1
    for i in range(3):
        record = Sensor_Record(
            timestamp=datetime.utcnow() - timedelta(hours=i),
            value=20 + i,
            sensor=sensor1,
            parameter=param
        )
        db.session.add(record)
    
    # Добавляем одну запись для sensor2
    record = Sensor_Record(
        timestamp=datetime.utcnow(),
        value=30.0,
        sensor=sensor2,
        parameter=param
    )
    db.session.add(record)
    db.session.commit()

    # Запрашиваем записи для sensor1
    response = client.get(url_for('sensor_records.show_sensor_records', sensor_id=sensor1.id))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert all(record['sensor_id'] == 'Sensor 1' for record in data)

def test_show_sensor_records_raw_data(client, init_database):
    """Тест получения сырых данных с фильтрацией по дате"""
    sensor = Sensor(name="Test Sensor")
    param = Parameter(name="Temperature", unit="C")
    db.session.add_all([sensor, param])
    
    now = datetime.utcnow()
    dates = [now - timedelta(days=i) for i in range(3)]
    
    for i, date in enumerate(dates):
        record = Sensor_Record(
            timestamp=date,
            value=20 + i,
            sensor=sensor,
            parameter=param
        )
        db.session.add(record)
    db.session.commit()

    # Форматируем даты для запроса
    start_date = formatdate(dates[1].timestamp())
    end_date = dates[2].strftime('%Y-%m-%d')

    # Запрос с фильтрацией по дате
    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=sensor.id),
        query_string={'start_date': start_date, 'end_date': end_date}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # Должны получить 2 записи в этом интервале
    assert set(data) == {21.0, 22.0}

# =====================
# NEGATIVE TESTS
# =====================

def test_show_sensor_records_empty_db(client, init_database):
    """Тест получения записей из пустой БД"""
    response = client.get(url_for('sensor_records.show_all_sensor_records'))
    assert response.status_code == 200
    assert response.get_json() == []

def test_show_sensor_records_nonexistent_sensor(client, init_database):
    """Тест получения записей несуществующего сенсора"""
    response = client.get(url_for('sensor_records.show_sensor_records', sensor_id=999))
    assert response.status_code == 200
    assert response.get_json() == []

def test_show_sensor_records_raw_data_invalid_dates(client, init_database):
    """Тест с некорректными форматами дат"""
    sensor = Sensor(name="Test Sensor")
    db.session.add(sensor)
    db.session.commit()

    # Неправильный формат start_date
    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=sensor.id),
        query_string={'start_date': 'invalid-date'}
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.get_json()['error']

    # Неправильный формат end_date
    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=sensor.id),
        query_string={'end_date': 'invalid-date'}
    )
    assert response.status_code == 400
    assert "Invalid end_date format" in response.get_json()['error']

def test_show_sensor_records_raw_data_invalid_parameter(client, init_database):
    """Тест с несуществующим параметром"""
    sensor = Sensor(name="Test Sensor")
    db.session.add(sensor)
    db.session.commit()

    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=sensor.id),
        query_string={'parameter': 'nonexistent'}
    )
    assert response.status_code == 200
    assert response.get_json() == []  # Должен вернуть пустой список

def test_show_sensor_records_raw_data_nonexistent_sensor(client, init_database):
    """Тест с несуществующим сенсором"""
    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=999)
    )
    assert response.status_code == 200
    assert response.get_json() == []  # Должен вернуть пустой список
