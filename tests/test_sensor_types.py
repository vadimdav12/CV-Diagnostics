# backend/tests/test_sensor_types.py

def test_show_sensor_types(client):
    response = client.get('/sensor-type/')
    assert response.status_code == 200

def test_add_sensor_type(client):
    response = client.post('/sensor-type/add', json={"name": "Temperature"})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Temperature"

def test_update_sensor_type(client):
    response = client.post('/sensor-type/add', json={"name": "Humidity"})
    sensor_type_id = response.get_json()['id']

    response = client.put(f'/sensor-type/{sensor_type_id}', json={"name": "Updated Humidity"})
    assert response.status_code == 200
    assert response.get_json()['name'] == "Updated Humidity"

def test_delete_sensor_type(client):
    response = client.post('/sensor-type/add', json={"name": "Pressure"})
    sensor_type_id = response.get_json()['id']

    response = client.delete(f'/sensor-type/{sensor_type_id}')
    assert response.status_code == 200
