import pytest
from flask import url_for
from datetime import datetime, timedelta
from email.utils import formatdate
from app import create_app, db
from app.models.equipment import Equipment
from app.models.sensor import Sensor
from app.models.sensor_type import Sensor_type
from app.models.parameter import Parameter
from app.models.sensor_parameter import Sensor_parameter
from app.models.sensor_record import Sensor_record
from app.models.users import User, Role
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

# Фикстура для создания тестового приложения
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# Фикстура для тестового клиента
@pytest.fixture
def client(app):
    return app.test_client()

# Фикстура для авторизационных заголовков
@pytest.fixture
def auth_headers(app):
    with app.app_context():
        # Создаем тестового пользователя
        role = Role(name='admin')
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass')
        )
        user.roles.append(role)
        db.session.add(role)
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}

# Фикстура для второго пользователя
@pytest.fixture
def second_user_auth_headers(app):
    with app.app_context():
        # Создаем второго тестового пользователя
        role = Role.query.first() or Role(name='admin')
        user = User(
            username='seconduser',
            email='second@example.com',
            password_hash=generate_password_hash('secondpass')
        )
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}

# Тест полного сценария: создание оборудования, датчика, параметра и записи сенсора
def test_create_equipment_sensor_and_record(client, auth_headers):
    """Позитивный интеграционный тест: создание оборудования, датчика, параметра и записи сенсора"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    assert response.status_code == 201
    equipment_id = response.get_json()['id']

    # 2. Создаем тип датчика
    sensor_type_data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=sensor_type_data, headers=auth_headers)
    assert response.status_code == 201
    sensor_type_id = response.get_json()['id']

    # 3. Создаем датчик для оборудования
    sensor_data = {
        'name': 'Test Sensor',
        'data_source': 'test_source',
        'sensor_type_id': sensor_type_id
    }
    response = client.post(f'/api/equipment/{equipment_id}/sensors', json=sensor_data, headers=auth_headers)
    assert response.status_code == 201
    sensor_id = response.get_json()['id']

    # 4. Создаем параметр
    parameter_data = {'name': 'Temperature', 'unit': 'C'}
    response = client.post(url_for('parameter.add_sensor'), json=parameter_data, headers=auth_headers)
    assert response.status_code == 201
    parameter_id = response.get_json()['id']

    # 5. Создаем связь sensor_parameter
    sensor_parameter_data = {
        'key': 'temp_key',
        'sensor_id': sensor_id,
        'parameter_id': parameter_id
    }
    response = client.post('/sensors_parameters/add', json=sensor_parameter_data, headers=auth_headers)
    assert response.status_code == 201
    sensor_parameter_id = response.get_json()['id']

    # 6. Создаем запись сенсора
    record_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'value': 25.5,
        'sensor_id': sensor_id,
        'parameter_id': parameter_id
    }
    response = client.post(url_for('sensor_records.add_sensor_record'), json=record_data, headers=auth_headers)
    assert response.status_code == 201

    # Проверяем, что запись сенсора появилась в базе
    response = client.get(url_for('sensor_records.show_sensor_records', sensor_id=sensor_id), headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['value'] == 25.5
    assert data[0]['sensor_id'] == sensor_id
    assert data[0]['parameter_id'] == parameter_id

# Тест фильтрации записей сенсоров по датчику, параметру и диапазону дат
def test_filter_sensor_records(client, auth_headers):
    """Позитивный интеграционный тест: фильтрация записей сенсоров"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    equipment_id = response.get_json()['id']

    # 2. Создаем тип датчика
    sensor_type_data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=sensor_type_data, headers=auth_headers)
    sensor_type_id = response.get_json()['id']

    # 3. Создаем датчик
    sensor_data = {
        'name': 'Test Sensor',
        'data_source': 'test_source',
        'sensor_type_id': sensor_type_id
    }
    response = client.post(f'/api/equipment/{equipment_id}/sensors', json=sensor_data, headers=auth_headers)
    sensor_id = response.get_json()['id']

    # 4. Создаем параметр
    parameter_data = {'name': 'Temperature', 'unit': 'C'}
    response = client.post(url_for('parameter.add_sensor'), json=parameter_data, headers=auth_headers)
    parameter_id = response.get_json()['id']

    # 5. Создаем несколько записей сенсора
    now = datetime.utcnow()
    dates = [now - timedelta(days=i) for i in range(3)]
    for i, date in enumerate(dates):
        record = Sensor_record(
            timestamp=date,
            value=20 + i,
            sensor_id=sensor_id,
            parameter_id=parameter_id
        )
        db.session.add(record)
    db.session.commit()

    # 6. Фильтруем записи по диапазону дат
    start_date = formatdate(dates[1].timestamp())  # вчера
    end_date = dates[2].strftime('%Y-%m-%d')       # позавчера
    response = client.get(
        url_for('sensor_records.show_sensor_records_raw_data', sensor_id=sensor_id),
        query_string={'start_date': start_date, 'end_date': end_date, 'parameter': 'Temperature'},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert set(record['value'] for record in data) == {21.0, 22.0}

# Негативный тест: попытка удаления оборудования с привязанными датчиками
def test_delete_equipment_with_sensors(client, auth_headers):
    """Негативный интеграционный тест: удаление оборудования с датчиками"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    equipment_id = response.get_json()['id']

    # 2. Создаем тип датчика
    sensor_type_data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=sensor_type_data, headers=auth_headers)
    sensor_type_id = response.get_json()['id']

    # 3. Создаем датчик
    sensor_data = {
        'name': 'Test Sensor',
        'data_source': 'test_source',
        'sensor_type_id': sensor_type_id
    }
    response = client.post(f'/api/equipment/{equipment_id}/sensors', json=sensor_data, headers=auth_headers)
    assert response.status_code == 201

    # 4. Пытаемся удалить оборудование
    response = client.delete(f'/api/equipment/{equipment_id}', headers=auth_headers)
    assert response.status_code == 400
    assert 'referenced' in response.get_json()['error']
    assert 'sensors' in response.get_json()['error']

# Тест доступа к данным оборудования с авторизацией
def test_access_equipment_with_auth(client, auth_headers):
    """Позитивный интеграционный тест: доступ к данным оборудования с авторизацией"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    assert response.status_code == 201
    equipment_id = response.get_json()['id']

    # 2. Проверяем доступ к списку оборудования
    response = client.get('/api/equipment/', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Test Equipment'

    # 3. Проверяем доступ к конкретному оборудованию
    response = client.get(f'/api/equipment/{equipment_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Test Equipment'

# Негативный тест: доступ к данным оборудования без авторизации
def test_access_equipment_without_auth(client):
    """Негативный интеграционный тест: доступ к данным без авторизации"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data)  # Без заголовков авторизации
    assert response.status_code in (401, 403)  # Ожидаем ошибку авторизации

    # 2. Проверяем доступ к списку оборудования
    response = client.get('/api/equipment/')
    assert response.status_code in (401, 403)

    # 3. Проверяем доступ к конкретному оборудованию
    response = client.get('/api/equipment/1')
    assert response.status_code in (401, 403)

# Тест создания и обновления конфигурации датчика с параметрами
def test_configure_and_update_sensor_parameters(client, auth_headers):
    """Позитивный интеграционный тест: создание и обновление конфигурации датчика"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    equipment_id = response.get_json()['id']

    # 2. Создаем тип датчика
    sensor_type_data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=sensor_type_data, headers=auth_headers)
    sensor_type_id = response.get_json()['id']

    # 3. Создаем датчик
    sensor_data = {
        'name': 'Test Sensor',
        'data_source': 'test_source',
        'sensor_type_id': sensor_type_id
    }
    response = client.post(f'/api/equipment/{equipment_id}/sensors', json=sensor_data, headers=auth_headers)
    sensor_id = response.get_json()['id']

    # 4. Создаем два параметра
    param1_data = {'name': 'Temperature', 'unit': 'C'}
    response = client.post(url_for('parameter.add_sensor'), json=param1_data, headers=auth_headers)
    param1_id = response.get_json()['id']

    param2_data = {'name': 'Humidity', 'unit': '%'}
    response = client.post(url_for('parameter.add_sensor'), json=param2_data, headers=auth_headers)
    param2_id = response.get_json()['id']

    # 5. Создаем связи sensor_parameter
    sp1_data = {'key': 'temp_key', 'sensor_id': sensor_id, 'parameter_id': param1_id}
    response = client.post('/sensors_parameters/add', json=sp1_data, headers=auth_headers)
    assert response.status_code == 201
    sp1_id = response.get_json()['id']

    sp2_data = {'key': 'humid_key', 'sensor_id': sensor_id, 'parameter_id': param2_id}
    response = client.post('/sensors_parameters/add', json=sp2_data, headers=auth_headers)
    assert response.status_code == 201
    sp2_id = response.get_json()['id']

    # 6. Обновляем один из параметров
    update_sp1_data = {'key': 'updated_temp_key', 'sensor_id': sensor_id, 'parameter_id': param1_id}
    response = client.put(f'/sensors_parameters/{sp1_id}', json=update_sp1_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['key'] == 'updated_temp_key'

    # 7. Проверяем, что конфигурация датчика обновлена корректно
    response = client.get('/sensors_parameters/', headers=auth_headers)
    data = response.get_json()
    assert len(data) == 2
    assert any(sp['key'] == 'updated_temp_key' and sp['sensor_id'] == sensor_id for sp in data)
    assert any(sp['key'] == 'humid_key' and sp['sensor_id'] == sensor_id for sp in data)

# Тест доступа второго пользователя к оборудованию, созданному первым
def test_user_access_to_other_user_equipment(client, auth_headers, second_user_auth_headers):
    """Интеграционный тест: проверка доступа второго пользователя к оборудованию"""
    # 1. Первый пользователь создает оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    assert response.status_code == 201
    equipment_id = response.get_json()['id']

    # 2. Второй пользователь пытается получить доступ к оборудованию
    response = client.get(f'/api/equipment/{equipment_id}', headers=second_user_auth_headers)
    assert response.status_code == 200  # Предполагаем, что доступ разрешен для пользователей с ролью admin
    assert response.get_json()['name'] == 'Test Equipment'

    # 3. Второй пользователь пытается обновить оборудование
    update_data = {'name': 'Updated Equipment'}
    response = client.put(f'/api/equipment/{equipment_id}', json=update_data, headers=second_user_auth_headers)
    assert response.status_code == 200  # Предполагаем, что обновление разрешено
    assert response.get_json()['name'] == 'Updated Equipment'

# Тест фильтрации записей сенсоров по нескольким параметрам
def test_filter_sensor_records_multiple_parameters(client, auth_headers):
    """Позитивный интеграционный тест: фильтрация записей по нескольким параметрам"""
    # 1. Создаем оборудование
    equipment_data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', json=equipment_data, headers=auth_headers)
    equipment_id = response.get_json()['id']

    # 2. Создаем тип датчика
    sensor_type_data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=sensor_type_data, headers=auth_headers)
    sensor_type_id = response.get_json()['id']

    # 3. Создаем датчик
    sensor_data = {
        'name': 'Test Sensor',
        'data_source': 'test_source',
        'sensor_type_id': sensor_type_id
    }
    response = client.post(f'/api/equipment/{equipment_id}/sensors', json=sensor_data, headers=auth_headers)
    sensor_id = response.get_json()['id']

    # 4. Создаем два параметра
    param1_data = {'name': 'Temperature', 'unit': 'C'}
    response = client.post(url_for('parameter.add_sensor'), json=param1_data, headers=auth_headers)
    param1_id = response.get_json()['id']

    param2_data = {'name': 'Humidity', 'unit': '%'}
    response = client.post(url_for('parameter.add_sensor'), json=param2_data, headers=auth_headers)
    param2_id = response.get_json()['id']

    # 5. Создаем записи сенсора для разных параметров
    now = datetime.utcnow()
    record1 = Sensor_record(
        timestamp=now,
        value=25.5,
        sensor_id=sensor_id,
        parameter_id=param1_id
    )
    record2 = Sensor_record(
        timestamp=now - timedelta(hours=1),
        value=60.0,
        sensor_id=sensor_id,
        parameter_id=param2_id
    )
    db.session.add_all([record1, record2])
    db.session.commit()

    # 6. Фильтруем записи по обоим параметрам
    response = client.get(
        url_for('sensor_records.show_sensor_records', sensor_id=sensor_id),
        query_string={'parameter': 'Temperature,Humidity'},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert any(record['value'] == 25.5 and record['parameter_id'] == param1_id for record in data)
    assert any(record['value'] == 60.0 and record['parameter_id'] == param2_id for record in data)

# Негативный тест: создание записи сенсора с несуществующим датчиком или параметром
def test_create_sensor_record_invalid_references(client, auth_headers):
    """Негативный интеграционный тест: создание записи сенсора с несуществующими ссылками"""
    # 1. Пытаемся создать запись с несуществующим датчиком
    record_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'value': 25.5,
        'sensor_id': 999,  # Несуществующий датчик
        'parameter_id': 1
    }
    response = client.post(url_for('sensor_records.add_sensor_record'), json=record_data, headers=auth_headers)
    assert response.status_code == 400
    assert 'not found' in response.get_json()['error'].lower()

    # 2. Пытаемся создать запись с несуществующим параметром
    record_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'value': 25.5,
        'sensor_id': 1,
        'parameter_id': 999  # Несуществующий параметр
    }
    response = client.post(url_for('sensor_records.add_sensor_record'), json=record_data, headers=auth_headers)
    assert response.status_code == 400
    assert 'not found' in response.get_json()['error'].lower()