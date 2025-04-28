import pytest
from app import create_app, db
from app.models.sensor_parameter import Sensor_parameter
from app.models.sensor import Sensor
from app.models.parameter import Parameter

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Создаем тестовые данные
        sensor = Sensor(name="Test Sensor")
        parameter = Parameter(name="Test Parameter")
        db.session.add(sensor)
        db.session.add(parameter)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_sensor_parameter(app):
    with app.app_context():
        sensor = Sensor.query.first()
        parameter = Parameter.query.first()
        sp = Sensor_parameter(key="test_key", sensor_id=sensor.id, parameter_id=parameter.id)
        db.session.add(sp)
        db.session.commit()
        return sp

def test_show_sensors_parameters(client, test_sensor_parameter):
    # Позитивный тест
    response = client.get('/sensors_parameters/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['id'] == test_sensor_parameter.id
    assert data[0]['key'] == 'test_key'

def test_add_sensor_parameter_valid(client):
    # Позитивный тест добавления
    sensor = Sensor.query.first()
    parameter = Parameter.query.first()
    data = {
        'key': 'new_key',
        'sensor_id': sensor.id,
        'parameter_id': parameter.id
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data['key'] == 'new_key'
    assert response_data['sensor_id'] == sensor.id
    assert response_data['parameter_id'] == parameter.id

def test_add_sensor_parameter_missing_fields(client):
    # Негативный тест - отсутствуют обязательные поля
    # 1. Отсутствует key
    data = {
        'sensor_id': 1,
        'parameter_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400
    
    # 2. Отсутствует sensor_id
    data = {
        'key': 'test',
        'parameter_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400
    
    # 3. Отсутствует parameter_id
    data = {
        'key': 'test',
        'sensor_id': 1
    }
    response = client.post('/sensors_parameters/add', json=data)
    assert response.status_code == 400
    
    # 4. Пустой запрос
    response = client.post('/sensors_parameters/add', json={})
    assert response.status_code == 400

def test_update_sensor_parameter_valid(client, test_sensor_parameter):
    # Позитивный тест обновления
    update_data = {
        'key': 'updated_key',
        'sensor_id': test_sensor_parameter.sensor_id,
        'parameter_id': test_sensor_parameter.parameter_id
    }
    response = client.put(f'/sensors_parameters/{test_sensor_parameter.id}', json=update_data)
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['key'] == 'updated_key'

def test_update_sensor_parameter_invalid(client):
    # Негативные тесты обновления
    # 1. Несуществующий ID
    response = client.put('/sensors_parameters/9999', json={'key': 'test'})
    assert response.status_code == 404
    
    # 2. Пустой запрос
    response = client.put(f'/sensors_parameters/1', json={})
    assert response.status_code == 400

def test_delete_sensor_parameter_valid(client, test_sensor_parameter):
    # Позитивный тест удаления
    response = client.delete(f'/sensors_parameters/{test_sensor_parameter.id}')
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['message'] == 'Sensor_parameter deleted successfully'
    
    # Проверяем, что действительно удалено
    response = client.get(f'/sensors_parameters/{test_sensor_parameter.id}')
    assert response.status_code == 404

def test_delete_sensor_parameter_invalid(client):
    # Негативный тест удаления - несуществующий ID
    response = client.delete('/sensors_parameters/9999')
    assert response.status_code == 404