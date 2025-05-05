# Импорт необходимых модулей и библиотек
import pytest
from flask import jsonify, url_for  # Для работы с JSON и генерации URL
from backend.app.models.parameter import Parameter  # Модель параметра
from backend.app import db  # Объект базы данных


def test_show_parameters(client, init_database):
    """Позитивный тест получения списка параметров (успешный сценарий)"""
    # Создаем тестовые параметры в базе данных
    param1 = Parameter(name="Temperature", unit="C")
    param2 = Parameter(name="Humidity", unit="%")
    db.session.add(param1)
    db.session.add(param2)
    db.session.commit()

    # Отправляем GET запрос на эндпоинт показа параметров
    response = client.get(url_for('parameter.show_parameter'))
    
    # Проверяем, что сервер вернул код 200 (OK)
    assert response.status_code == 200
    
    # Получаем и проверяем данные ответа
    data = response.get_json()
    assert len(data) == 2  # Должны вернуться 2 параметра
    # Проверяем наличие ожидаемых параметров в ответе
    assert {'id': 1, 'name': 'Temperature', 'unit': 'C'} in data
    assert {'id': 2, 'name': 'Humidity', 'unit': '%'} in data

def test_add_parameter_success(client, init_database):
    """Позитивный тест добавления параметра (успешный сценарий)"""
    # Подготавливаем данные для нового параметра
    data = {'name': 'Pressure', 'unit': 'hPa'}
    
    # Отправляем POST запрос на добавление параметра
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    
    # Проверяем ответ сервера
    assert response.status_code == 201  # Код 201 (Created)
    response_data = response.get_json()
    assert 'id' in response_data  # В ответе должен быть ID созданного параметра
    assert response_data['name'] == 'Pressure'  # Проверяем имя
    assert response_data['unit'] == 'hPa'  # Проверяем единицы измерения

    # Дополнительная проверка - убеждаемся, что параметр действительно добавлен в БД
    param = Parameter.query.filter_by(name='Pressure').first()
    assert param is not None
    assert param.unit == 'hPa'

def test_update_parameter_success(client, init_database):
    """Позитивный тест обновления параметра (успешный сценарий)"""
    # Создаем параметр для обновления
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Подготавливаем данные для обновления
    data = {'name': 'Temp', 'unit': 'K'}
    
    # Отправляем PUT запрос на обновление параметра
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    
    # Проверяем ответ сервера
    assert response.status_code == 200  # Код 200 (OK)
    response_data = response.get_json()
    assert response_data['name'] == 'Temp'  # Проверяем новое имя
    assert response_data['unit'] == 'K'  # Проверяем новые единицы измерения

    # Проверяем, что параметр действительно обновлен в БД
    updated_param = Parameter.query.get(param.id)
    assert updated_param.name == 'Temp'
    assert updated_param.unit == 'K'

def test_delete_parameter_success(client, init_database):
    """Позитивный тест удаления параметра (успешный сценарий)"""
    # Создаем параметр для удаления
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Отправляем DELETE запрос на удаление параметра
    response = client.delete(
        url_for('parameter.delete_sensor', parameter_id=param.id)
    )
    
    # Проверяем ответ сервера
    assert response.status_code == 200  # Код 200 (OK)
    assert 'Parameter deleted successfully' in response.get_json()['message']

    # Проверяем, что параметр действительно удален из БД
    assert Parameter.query.get(param.id) is None



def test_show_parameters_empty_db(client, init_database):
    """Негативный тест получения списка параметров из пустой БД"""
    response = client.get(url_for('parameter.show_parameter'))
    assert response.status_code == 200  # Должен вернуть 200 даже при пустой БД
    assert response.get_json() == []  # Должен вернуть пустой список

def test_add_parameter_missing_fields(client, init_database):
    """Негативный тест добавления параметра с отсутствующими полями"""
    # Тест 1: Отсутствует поле 'unit'
    data = {'name': 'Pressure'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400  # Код 400 (Bad Request)
    assert 'name and unit are required' in response.get_json()['error']

    # Тест 2: Отсутствует поле 'name'
    data = {'unit': 'hPa'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400
    assert 'name and unit are required' in response.get_json()['error']

def test_add_parameter_empty_json(client, init_database):
    """Негативный тест добавления параметра с пустым JSON"""
    response = client.post(
        url_for('parameter.add_sensor'),
        json={}
    )
    assert response.status_code == 400
    assert 'name and unit are required' in response.get_json()['error']

def test_add_parameter_duplicate_name(client, init_database):
    """Негативный тест добавления параметра с дублирующимся именем"""
    # Создаем параметр в БД
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Пытаемся создать параметр с таким же именем
    data = {'name': 'Temperature', 'unit': 'K'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400
    assert 'Parameter already exists' in response.get_json()['error']

def test_add_parameter_invalid_types(client, init_database):
    """Негативный тест добавления параметра с некорректными типами данных"""
    # Тест 1: Число вместо строки для name
    data = {'name': 123, 'unit': 'hPa'}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400  # Ожидаем ошибку валидации

    # Тест 2: Список вместо строки для unit
    data = {'name': 'Pressure', 'unit': ['hPa']}
    response = client.post(
        url_for('parameter.add_sensor'),
        json=data
    )
    assert response.status_code == 400

def test_update_parameter_not_found(client, init_database):
    """Негативный тест обновления несуществующего параметра"""
    data = {'name': 'Temp', 'unit': 'K'}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=999),  # Несуществующий ID
        json=data
    )
    assert response.status_code == 404  # Код 404 (Not Found)

def test_update_parameter_duplicate_name(client, init_database):
    """Негативный тест обновления параметра с дублирующимся именем"""
    # Создаем два параметра
    param1 = Parameter(name="Temperature", unit="C")
    param2 = Parameter(name="Humidity", unit="%")
    db.session.add(param1)
    db.session.add(param2)
    db.session.commit()

    # Пытаемся изменить имя второго параметра на имя первого
    data = {'name': 'Temperature'}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param2.id),
        json=data
    )
    assert response.status_code == 400
    assert 'name already exists' in response.get_json()['error']

def test_update_parameter_empty_json(client, init_database):
    """Негативный тест обновления параметра с пустым JSON"""
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json={}  # Пустой JSON
    )
    assert response.status_code == 400
    assert 'No data provided' in response.get_json()['error']

def test_update_parameter_invalid_types(client, init_database):
    """Негативный тест обновления параметра с некорректными типами данных"""
    param = Parameter(name="Temperature", unit="C")
    db.session.add(param)
    db.session.commit()

    # Тест 1: Число вместо строки для name
    data = {'name': 123}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    assert response.status_code == 400

    # Тест 2: Словарь вместо строки для unit
    data = {'unit': {'value': 'K'}}
    response = client.put(
        url_for('parameter.update_sensor', parameter_id=param.id),
        json=data
    )
    assert response.status_code == 400

def test_delete_parameter_not_found(client, init_database):
    """Негативный тест удаления несуществующего параметра"""
    response = client.delete(
        url_for('parameter.delete_sensor', parameter_id=999)  # Несуществующий ID
    )
    assert response.status_code == 404  # Код 404 (Not Found)