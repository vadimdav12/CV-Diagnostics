# Импортируем необходимые библиотеки и модули
import pytest
from app import create_app, db
from app.models.sensor_parameter import Sensor_parameter
from app.models.sensor import Sensor
from app.models.parameter import Parameter

# Фикстура для создания приложения в тестовом окружении
@pytest.fixture
def app():
    app = create_app('testing')  # Создание приложения с конфигурацией 'testing'
    with app.app_context():
        db.create_all()  # Инициализация всех таблиц базы данных

        # Создаем тестовые записи: один сенсор и один параметр
        sensor = Sensor(name="Test Sensor")
        parameter = Parameter(name="Test Parameter")
        db.session.add(sensor)
        db.session.add(parameter)
        db.session.commit()

        yield app  # Передаём приложение тестам

        # После тестов — очистка базы
        db.session.remove()
        db.drop_all()

# Фикстура для создания тестового клиента Flask
@pytest.fixture
def client(app):
    return app.test_client()

# Фикстура для создания тестовой записи Sensor_parameter
@pytest.fixture
def test_sensor_parameter(app):
    with app.app_context():
        sensor = Sensor.query.first()
        parameter = Parameter.query.first()

        # Создаем и сохраняем объект Sensor_parameter
        sp = Sensor_parameter(key="test_key", sensor_id=sensor.id, parameter_id=parameter.id)
        db.session.add(sp)
        db.session.commit()
        return sp

# Тест получения списка всех sensor_parameter
def test_show_sensors_parameters(client, test_sensor_parameter):
    """Позитивный тест - список должен содержать ранее созданную запись"""
    response = client.get('/sensors_parameters/')
    assert response.status_code == 200  # Успешный ответ
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['id'] == test_sensor_parameter.id
    assert data[0]['key'] == 'test_key'

# Тест добавления новой записи sensor_parameter
def test_add_sensor_parameter_valid(client):
    """Позитивный тест - добавление новой записи"""
    sensor = Sensor.query.first()
    parameter = Parameter.query.first()
    data = {
        'key': 'new_key',
        'sensor_id': sensor.id,
        'parameter_id': parameter.id
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 201  # Ожидаем код "создано"
    response_data = response.get_json()
    assert response_data['key'] == 'new_key'
    assert response_data['sensor_id'] == sensor.id
    assert response_data['parameter_id'] == parameter.id

# Негативные тесты — отправка неполных данных при создании
def test_add_sensor_parameter_missing_fields(client):
    """Негативный тест - отправка неполных данных при создании"""
    # 1. Нет ключа
    data = {
        'sensor_id': 1,
        'parameter_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400

    # 2. Нет sensor_id
    data = {
        'key': 'test',
        'parameter_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400

    # 3. Нет parameter_id
    data = {
        'key': 'test',
        'sensor_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400

    # 4. Пустой запрос
    response = client.post('/sensors_parameters/add', json={})
    assert response.status_code == 400

# Тест обновления существующей записи
def test_update_sensor_parameter_valid(client, test_sensor_parameter):
    """Позитивный тест - обновляем ключ"""
    update_data = {
        'key': 'updated_key',
        'sensor_id': test_sensor_parameter.sensor_id,
        'parameter_id': test_sensor_parameter.parameter_id
    }
    response = client.put(f'/sensors_parameters/{test_sensor_parameter.id}', json=update_data)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['key'] == 'updated_key'

# Негативные тесты для обновления
def test_update_sensor_parameter_invalid(client):
    """Негативный тест - несуществующее ID"""
    # 1. Обновление по несуществующему ID
    response = client.put('/sensors_parameters/9999', json={'key': 'test'})
    assert response.status_code == 404

    # 2. Пустой запрос
    response = client.put(f'/sensors_parameters/1', json={})
    assert response.status_code == 400

# Успешное удаление sensor_parameter
def test_delete_sensor_parameter_valid(client, test_sensor_parameter):
    """Позитивный тест - успешное удаление sensor_parameter"""
    # Удаляем запись
    response = client.delete(f'/sensors_parameters/{test_sensor_parameter.id}')
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['message'] == 'Sensor_parameter deleted successfully'

    # Проверяем, что запись больше не существует
    response = client.get(f'/sensors_parameters/{test_sensor_parameter.id}')
    assert response.status_code == 404

# Негативный тест — удаление несуществующей записи
def test_delete_sensor_parameter_invalid(client):
    """Негативный тест - удаление несуществующей записи"""
    response = client.delete('/sensors_parameters/9999')
    assert response.status_code == 404
