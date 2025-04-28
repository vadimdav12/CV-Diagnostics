import pytest
from app import create_app, db
from app.models.equipment import Equipment
from app.models.sensor import Sensor
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Создаем тестовые данные
        eq = Equipment(name="Test Equipment")
        db.session.add(eq)
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

def test_show_equipment(client, auth_headers):
    """Позитивный тест получения списка оборудования"""
    response = client.get('/api/equipment/', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == "Test Equipment"

def test_add_equipment_valid(client, auth_headers):
    """Позитивный тест добавления оборудования"""
    data = {'name': 'New Equipment'}
    response = client.post('/api/equipment/add', 
                         json=data,
                         headers=auth_headers)
    assert response.status_code == 201
    assert response.get_json()['name'] == 'New Equipment'

def test_add_equipment_missing_name(client, auth_headers):
    """Негативный тест - отсутствует обязательное поле name"""
    response = client.post('/api/equipment/add', 
                         json={},
                         headers=auth_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_add_equipment_duplicate_name(client, auth_headers):
    """Негативный тест - дублирование имени оборудования"""
    data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', 
                         json=data,
                         headers=auth_headers)
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['error']

def test_update_equipment_valid(client, auth_headers):
    """Позитивный тест обновления оборудования"""
    equipment = Equipment.query.first()
    data = {'name': 'Updated Name'}
    response = client.put(f'/api/equipment/{equipment.id}', 
                        json=data,
                        headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Name'

def test_update_equipment_invalid_id(client, auth_headers):
    """Негативный тест - несуществующий ID оборудования"""
    response = client.put('/api/equipment/9999', 
                        json={'name': 'Test'},
                        headers=auth_headers)
    assert response.status_code == 404

def test_delete_equipment_valid(client, auth_headers):
    """Позитивный тест удаления оборудования"""
    equipment = Equipment.query.first()
    response = client.delete(f'/api/equipment/{equipment.id}',
                           headers=auth_headers)
    assert response.status_code == 200
    assert 'deleted' in response.get_json()['message']

def test_delete_equipment_with_sensors(client, auth_headers):
    """Негативный тест - удаление оборудования с привязанными датчиками"""
    equipment = Equipment.query.first()
    sensor = Sensor(name="Test Sensor", equipment_id=equipment.id)
    db.session.add(sensor)
    db.session.commit()
    
    response = client.delete(f'/api/equipment/{equipment.id}',
                           headers=auth_headers)
    assert response.status_code == 400
    assert 'referenced' in response.get_json()['error']

def test_add_sensor_to_equipment_valid(client, auth_headers):
    """Позитивный тест добавления датчика к оборудованию"""
    equipment = Equipment.query.first()
    data = {
        'name': 'New Sensor',
        'data_source': 'test_source',
        'sensor_type_id': 1
    }
    response = client.post(f'/api/equipment/{equipment.id}/sensors',
                         json=data,
                         headers=auth_headers)
    assert response.status_code == 201
    assert response.get_json()['name'] == 'New Sensor'

def test_add_sensor_missing_fields(client, auth_headers):
    """Негативный тест - отсутствуют обязательные поля при добавлении датчика"""
    equipment = Equipment.query.first()
    data = {'name': 'Incomplete Sensor'}
    response = client.post(f'/api/equipment/{equipment.id}/sensors',
                         json=data,
                         headers=auth_headers)
    assert response.status_code == 400