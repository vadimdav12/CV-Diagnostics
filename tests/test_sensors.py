# backend/tests/test_sensors.py

def test_show_sensors(client):
    response = client.get('/sensors/')
    assert response.status_code == 200

def test_add_sensor(client, db):
    from app.models.equipment import Equipment
    from app.models.sensor_type import Sensor_type
    from app.models.sensor import Sensor

    # Создать связанные объекты для Foreign Key
    eq = Equipment(name="Equipment1")
    st = Sensor_type(name="SensorType1")
    db.session.add_all([eq, st])
    db.session.commit()

    sensor_data = {
        "name": "Sensor1",
        "data_source": "192.168.0.1",
        "sensor_type_id": st.id,
        "equipment_id": eq.id
    }
    response = client.post('/sensors/add', json=sensor_data)
    assert response.status_code == 201
    assert response.get_json()['name'] == "Sensor1"
