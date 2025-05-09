import pytest
from app import create_app, db
from app.models.users import User, Role
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

# Фикстура, создающая приложение с тестовой конфигурацией
@pytest.fixture
def app():
    app = create_app('testing')  # создаем приложение в режиме тестирования
    with app.app_context():
        db.create_all()  # создаем все таблицы в базе данных

        # Создаем роль "admin" и добавляем в БД
        role = Role(name='admin')
        db.session.add(role)

        # Создаем тестового пользователя
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass')  # хешируем пароль
        )
        user.roles.append(role)  # назначаем роль пользователю
        db.session.add(user)
        db.session.commit()  # сохраняем изменения в БД

        yield app  # передаем приложение в тесты

        # Очистка после завершения тестов
        db.session.remove()
        db.drop_all()

# Фикстура, возвращающая клиент для тестирования HTTP-запросов
@pytest.fixture
def client(app):
    return app.test_client()

# Фикстура, возвращающая заголовки с JWT-токеном для авторизации
@pytest.fixture
def auth_headers(app):
    with app.app_context():
        access_token = create_access_token(identity=1)  # создаем токен с ID=1
        return {'Authorization': f'Bearer {access_token}'}

# Тест получения списка пользователей
def test_show_users(client):
    """Позитивный тест получения списка пользователей"""
    response = client.get('/users/')  # отправляем GET-запрос
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # ожидаем список
    assert len(data) > 0
    assert data[0]['login'] == 'testuser'  # проверяем, что первый пользователь — testuser

# Тест получения списка ролей
def test_show_roles(client):
    """Позитивный тест получения списка ролей"""
    response = client.get('/users/roles/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]['name'] == 'admin'  # проверяем имя первой роли

# Тест добавления нового пользователя с корректными данными
def test_add_user_valid(client):
    """Позитивный тест добавления пользователя"""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass',
        'role': 'admin'
    }
    response = client.post('/users/add', json=data)
    assert response.status_code == 201  # пользователь успешно создан
    response_data = response.get_json()
    assert response_data['username'] == 'newuser'
    assert 'id' in response_data  # у ответа должен быть ID

# Тест добавления пользователя без обязательных полей
def test_add_user_missing_fields(client):
    """Негативный тест - отсутствуют обязательные поля"""
    test_cases = [
        ({'email': 'test@test.com', 'password': 'pass'}, 'Username'),  # нет username
        ({'username': 'test', 'password': 'pass'}, 'email'),          # нет email
        ({'username': 'test', 'email': 'test@test.com'}, 'password')  # нет password
    ]
    
    for data, missing_field in test_cases:
        response = client.post('/users/add', json=data)
        assert response.status_code == 400
        assert missing_field in response.get_json()['error']  # ожидаем сообщение об ошибке

# Тест добавления пользователя с дублирующимся username или email
def test_add_user_duplicate(client):
    """Негативный тест - дублирование username или email"""
    test_cases = [
        {'username': 'testuser', 'email': 'new@example.com', 'password': 'pass'},  # username уже существует
        {'username': 'newuser', 'email': 'test@example.com', 'password': 'pass'}   # email уже существует
    ]
    
    for data in test_cases:
        response = client.post('/users/add', json=data)
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']

# Тест обновления данных пользователя
def test_update_user_valid(client):
    """Позитивный тест обновления пользователя"""
    user = User.query.first()  # получаем первого пользователя
    data = {
        'username': 'updateduser',
        'email': 'updated@example.com'
    }
    response = client.put(f'/users/{user.id}', json=data)
    assert response.status_code == 200
    assert response.get_json()['username'] == 'updateduser'  # проверяем обновленные данные

# Тест попытки обновления пользователя на дублирующее значение
def test_update_user_duplicate(client):
    """Негативный тест - дублирование при обновлении"""
    # Добавляем второго пользователя
    new_user = User(username='user2', email='user2@example.com', password_hash='pass')
    db.session.add(new_user)
    db.session.commit()
    
    user = User.query.first()
    test_cases = [
        {'username': 'user2'},  # username уже занят
        {'email': 'user2@example.com'}  # email уже занят
    ]
    
    for data in test_cases:
        response = client.put(f'/users/{user.id}', json=data)
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['error']

# Тест удаления пользователя
def test_delete_user_valid(client):
    """Позитивный тест удаления пользователя"""
    user = User.query.first()
    response = client.delete(f'/users/{user.id}')
    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message']

# Тест получения JWT-токена с корректными учетными данными
def test_token_generation_valid(client):
    """Позитивный тест генерации токена"""
    data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    response = client.post('/users/token', json=data)
    assert response.status_code == 200
    assert 'access_token' in response.get_json()  # ожидаем наличие токена в ответе

# Тест генерации токена с ошибочными/неполными данными
def test_token_generation_invalid(client):
    """Негативные тесты генерации токена"""
    test_cases = [
        ({'password': 'pass'}, 'username'),  # отсутствует username
        ({'username': 'test'}, 'password'),  # отсутствует password
        ({'username': 'wrong', 'password': 'testpass'}, 'verify'),  # неправильный username
        ({'username': 'testuser', 'password': 'wrong'}, 'verify')   # неправильный password
    ]
    
    for data, error_keyword in test_cases:
        response = client.post('/users/token', json=data)
        assert response.status_code in (401, 403)  # доступ запрещен
        assert error_keyword in str(response.data)  # проверка содержимого ошибки

# Тест доступа к защищенному маршруту с авторизацией
def test_protected_route(client, auth_headers):
    """Тест защищенного маршрута"""
    response = client.get('/users/protected', headers=auth_headers)
    assert response.status_code == 200
    assert 'logged_in_as' in response.get_json()  # проверка, что пользователь успешно авторизован
