# backend/tests/test_users.py

def test_show_users(client, access_token):
    response = client.get('/users/', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_add_user(client, access_token):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password",
        "role": "admin"
    }
    response = client.post('/users/add', json=user_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.get_json()['username'] == "newuser"

def test_update_user(client, access_token, db):
    from app.models.users import User

    user = User(username="updateuser", email="updateuser@example.com", password_hash="hash")
    db.session.add(user)
    db.session.commit()

    response = client.put(f'/users/{user.id}', json={"username": "updateduser"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()['username'] == "updateduser"

def test_delete_user(client, access_token, db):
    from app.models.users import User

    user = User(username="deleteuser", email="deleteuser@example.com", password_hash="hash")
    db.session.add(user)
    db.session.commit()

    response = client.delete(f'/users/{user.id}', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
