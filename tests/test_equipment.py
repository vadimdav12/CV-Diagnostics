# backend/tests/test_equipment.py

def test_show_equipment(client, access_token):
    response = client.get('/api/equipment/', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_add_equipment(client, access_token):
    response = client.post('/api/equipment/add', json={"name": "Test Equipment"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Test Equipment"

def test_update_equipment(client, access_token):
    # Сначала создаём
    response = client.post('/api/equipment/add', json={"name": "Update Equipment"}, headers={"Authorization": f"Bearer {access_token}"})
    equipment_id = response.get_json()['id']

    # Потом обновляем
    response = client.put(f'/api/equipment/{equipment_id}', json={"name": "Updated Equipment"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()['name'] == "Updated Equipment"

def test_delete_equipment(client, access_token):
    response = client.post('/api/equipment/add', json={"name": "Delete Equipment"}, headers={"Authorization": f"Bearer {access_token}"})
    equipment_id = response.get_json()['id']

    response = client.delete(f'/api/equipment/{equipment_id}', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
