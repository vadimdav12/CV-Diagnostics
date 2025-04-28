import pytest
from app import create_app, db
from app.models.sensor_type import Sensor_type
from app.models.sensor import Sensor
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Создаем тестовые данные
        st = Sensor_type(name="Test Sensor Type")
        db.session.add(st)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        access_token = create_access_token(identity='test_user')
        return {'Authorization': f'Bearer {access_token}'}

def test_show_sensor_types(client):
    """Позитивный тест получения списка типов датчиков"""
    response = client.get('/sensor-type/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == "Test Sensor Type"

def test_add_sensor_type_valid(client):
    """Позитивный тест добавления типа датчика"""
    data = {'name': 'New Sensor Type'}
    response = client.post('/sensor-type/add', json=data)
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data['name'] == 'New Sensor Type'
    assert 'id' in response_data

def test_add_sensor_type_missing_name(client):
    """Негативный тест - отсутствует обязательное поле name"""
    response = client.post('/sensor-type/add', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert 'required' in response.get_json()['error']

def test_add_sensor_type_duplicate(client):
    """Негативный тест - дублирование имени типа датчика"""
    data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=data)
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['error']

def test_update_sensor_type_valid(client):
    """Позитивный тест обновления типа датчика"""
    sensor_type = Sensor_type.query.first()
    data = {'name': 'Updated Sensor Type'}
    response = client.put(f'/sensor-type/{sensor_type.id}', json=data)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Sensor Type'

def test_update_sensor_type_invalid_id(client):
    """Негативный тест - несуществующий ID типа датчика"""
    response = client.put('/sensor-type/9999', json={'name': 'Test'})
    assert response.status_code == 404

def test_update_sensor_type_duplicate_name(client):
    """Негативный тест - дублирование имени при обновлении"""
    # Создаем второй тип датчика
    st2 = Sensor_type(name="Another Type")
    db.session.add(st2)
    db.session.commit()
    
    sensor_type = Sensor_type.query.first()
    response = client.put(f'/sensor-type/{sensor_type.id}', 
                        json={'name': 'Another Type'})
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['error']

def test_delete_sensor_type_valid(client):
    """Позитивный тест удаления типа датчика"""
    sensor_type = Sensor_type.query.first()
    response = client.delete(f'/sensor-type/{sensor_type.id}')
    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message']

def test_delete_sensor_type_with_sensors(client):
    """Негативный тест - удаление типа с привязанными датчиками"""
    sensor_type = Sensor_type.query.first()
    # Создаем связанный датчик
    sensor = Sensor(name="Test Sensor", sensor_type_id=sensor_type.id)
    db.session.add(sensor)
    db.session.commit()
    
    response = client.delete(f'/sensor-type/{sensor_type.id}')
    assert response.status_code == 400
    assert 'referenced' in response.get_json()['error']
    assert 'sensors' in response.get_json()['error']

def test_delete_nonexistent_sensor_type(client):
    """Негативный тест - удаление несуществующего типа датчика"""
    response = client.delete('/sensor-type/9999')
    assert response.status_code == 404