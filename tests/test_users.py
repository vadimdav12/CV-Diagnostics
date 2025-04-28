import pytest
from app import create_app, db
from app.models.users import User, Role
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Создаем тестовые данные
        role = Role(name='admin')
        db.session.add(role)
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass')
        )
        user.roles.append(role)
        db.session.add(user)
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
        access_token = create_access_token(identity=1)  # ID тестового пользователя
        return {'Authorization': f'Bearer {access_token}'}

def test_show_users(client):
    """Позитивный тест получения списка пользователей"""
    response = client.get('/users/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['login'] == 'testuser'

def test_show_roles(client):
    """Позитивный тест получения списка ролей"""
    response = client.get('/users/roles/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]['name'] == 'admin'

def test_add_user_valid(client):
    """Позитивный тест добавления пользователя"""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass',
        'role': 'admin'
    }
    response = client.post('/users/add', json=data)
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data['username'] == 'newuser'
    assert 'id' in response_data

def test_add_user_missing_fields(client):
    """Негативный тест - отсутствуют обязательные поля"""
    test_cases = [
        ({'email': 'test@test.com', 'password': 'pass'}, 'Username'),  # Нет username
        ({'username': 'test', 'password': 'pass'}, 'email'),          # Нет email
        ({'username': 'test', 'email': 'test@test.com'}, 'password')  # Нет password
    ]
    
    for data, missing_field in test_cases:
        response = client.post('/users/add', json=data)
        assert response.status_code == 400
        assert missing_field in response.get_json()['error']

def test_add_user_duplicate(client):
    """Негативный тест - дублирование username или email"""
    test_cases = [
        {'username': 'testuser', 'email': 'new@example.com', 'password': 'pass'},  # Существующий username
        {'username': 'newuser', 'email': 'test@example.com', 'password': 'pass'}   # Существующий email
    ]
    
    for data in test_cases:
        response = client.post('/users/add', json=data)
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']

def test_update_user_valid(client):
    """Позитивный тест обновления пользователя"""
    user = User.query.first()
    data = {
        'username': 'updateduser',
        'email': 'updated@example.com'
    }
    response = client.put(f'/users/{user.id}', json=data)
    assert response.status_code == 200
    assert response.get_json()['username'] == 'updateduser'

def test_update_user_duplicate(client):
    """Негативный тест - дублирование при обновлении"""
    # Создаем второго пользователя
    new_user = User(username='user2', email='user2@example.com', password_hash='pass')
    db.session.add(new_user)
    db.session.commit()
    
    user = User.query.first()
    test_cases = [
        {'username': 'user2'},  # Существующий username
        {'email': 'user2@example.com'}  # Существующий email
    ]
    
    for data in test_cases:
        response = client.put(f'/users/{user.id}', json=data)
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']

def test_delete_user_valid(client):
    """Позитивный тест удаления пользователя"""
    user = User.query.first()
    response = client.delete(f'/users/{user.id}')
    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message']

def test_token_generation_valid(client):
    """Позитивный тест генерации токена"""
    data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    response = client.post('/users/token', json=data)
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_token_generation_invalid(client):
    """Негативные тесты генерации токена"""
    test_cases = [
        ({'password': 'pass'}, 'username'),  # Нет username
        ({'username': 'test'}, 'password'),  # Нет password
        ({'username': 'wrong', 'password': 'testpass'}, 'verify'),  # Неверный username
        ({'username': 'testuser', 'password': 'wrong'}, 'verify')   # Неверный password
    ]
    
    for data, error_keyword in test_cases:
        response = client.post('/users/token', json=data)
        assert response.status_code in (401, 403)
        assert error_keyword in str(response.data)

def test_protected_route(client, auth_headers):
    """Тест защищенного маршрута"""
    response = client.get('/users/protected', headers=auth_headers)
    assert response.status_code == 200
    assert 'logged_in_as' in response.get_json()