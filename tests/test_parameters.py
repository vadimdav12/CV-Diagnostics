import pytest
from flask import jsonify, url_for
from backend.app.models.parameter import Parameter
from backend.app import db

# =====================
# POSITIVE TESTS (нормальные сценарии)
# =====================

def test_show_parameters(client, init_database):
    """Тест получения списка параметров (успешный сценарий)"""
    # Создаем тестовые параметры
    param1 = Parameter(name="Temperature", unit="C")
    param2 = Parameter(name="Humidity", unit="%")
    db.session.add(param1)
    db.session.add(param2)
    db.session.commit()

    response = client.get(url_for('parameter.show_parameter'))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert {'id': 1, 'name': 'Temperature', 'unit': 'C'} in data
    assert {'id': 2, 'name': 'Humidity', 'unit': '%'} in data

def test_add_parameter_success(client, init_database):
    """Тест добавления параметра (успешный сценарий)"""
    data = {'name': 'Pressure', 'unit': 'hPa'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 201
    response_data = response.get_json()
    assert 'id' in response_data
    assert response_data['name'] == 'Pressure'
    assert response_data['unit'] == 'hPa'

    # Проверяем, что параметр действительно добавлен в БД
    param = Parameter.query.filter_by(name='Pressure').first()
    assert param is not None
    assert param.unit == 'hPa'

def test_update_parameter_success(client, init_database):
    """Тест обновления параметра (успешный сценарий)"""
    # Создаем параметр для обновления
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Обновляем параметр
    data = {'name': 'Temp', 'unit': 'K'}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['name'] == 'Temp'
    assert response_data['unit'] == 'K'

    # Проверяем, что параметр обновлен в БД
    updated_param = Parameter.query.get(param.id)
    assert updated_param.name == 'Temp'
    assert updated_param.unit == 'K'

def test_delete_parameter_success(client, init_database):
    """Тест удаления параметра (успешный сценарий)"""
    # Создаем параметр для удаления
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    response = client.delete(
        url_for('parameter.delete_sensor', parameter_id=param.id)
    )
    assert response.status_code == 200
    assert 'Parameter deleted successfully' in response.get_json()['message']

    # Проверяем, что параметр удален из БД
    assert Parameter.query.get(param.id) is None

# =====================
# NEGATIVE TESTS (негативные сценарии)
# =====================

def test_show_parameters_empty_db(client, init_database):
    """Тест получения списка параметров из пустой БД"""
    response = client.get(url_for('parameter.show_parameter'))
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_parameter_missing_fields(client, init_database):
    """Тест добавления параметра с отсутствующими полями"""
    # Нет поля 'unit'
    data = {'name': 'Pressure'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400
    assert 'name and unit are required' in response.get_json()['error']

    # Нет поля 'name'
    data = {'unit': 'hPa'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400
    assert 'name and unit are required' in response.get_json()['error']

def test_add_parameter_empty_json(client, init_database):
    """Тест добавления параметра с пустым JSON"""
    response = client.post(
        url_for('parameter.add_sensor'),
        json={}
    )
    assert response.status_code == 400
    assert 'name and unit are required' in response.get_json()['error']

def test_add_parameter_duplicate_name(client, init_database):
    """Тест добавления параметра с дублирующимся именем"""
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    data = {'name': 'Temperature', 'unit': 'K'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400
    assert 'Parameter already exists' in response.get_json()['error']

def test_add_parameter_invalid_types(client, init_database):
    """Тест добавления параметра с некорректными типами данных"""
    # Число вместо строки для name
    data = {'name': 123, 'unit': 'hPa'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400

    # Список вместо строки для unit
    data = {'name': 'Pressure', 'unit': ['hPa']}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400

def test_update_parameter_not_found(client, init_database):
    """Тест обновления несуществующего параметра"""
    data = {'name': 'Temp', 'unit': 'K'}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=999),
        json=data
    )
    assert response.status_code == 404

def test_update_parameter_duplicate_name(client, init_database):
    """Тест обновления параметра с дублирующимся именем"""
    param1 = Parameter(name="Temperature", unit="C")
    param2 = Parameter(name="Humidity", unit="%")
    db.session.add(param1)
    db.session.add(param2)
    db.session.commit()

    data = {'name': 'Temperature'}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param2.id),
        json=data
    )
    assert response.status_code == 400
    assert 'name already exists' in response.get_json()['error']

def test_update_parameter_empty_json(client, init_database):
    """Тест обновления параметра с пустым JSON"""
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json={}
    )
    assert response.status_code == 400
    assert 'No data provided' in response.get_json()['error']

def test_update_parameter_invalid_types(client, init_database):
    """Тест обновления параметра с некорректными типами данных"""
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Число вместо строки для name
    data = {'name': 123}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    assert response.status_code == 400

    # Словарь вместо строки для unit
    data = {'unit': {'value': 'K'}}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    assert response.status_code == 400

def test_delete_parameter_not_found(client, init_database):
    """Тест удаления несуществующего параметра"""
    response = client.delete(
        url_for('parameter.delete_sensor', parameter_id=999)
    )
    assert response.status_code == 404


