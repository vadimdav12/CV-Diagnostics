# Импорт необходимых модулей и библиотек
import pytest
from app import create_app, db  
from app.models.equipment import Equipment 
from app.models.sensor import Sensor  # Модель датчика
from flask_jwt_extended import create_access_token  

# Фикстура для создания тестового приложения
@pytest.fixture
def app():
    # Создаем приложение с конфигурацией для тестирования
    app = create_app('testing')
    
    # Работаем в контексте приложения
    with app.app_context():
        # Создаем все таблицы в базе данных
        db.create_all()
        
        # Создаем тестовые данные - одно оборудование
        eq = Equipment(name="Test Equipment")
        db.session.add(eq)
        db.session.commit()
        
        # Возвращаем приложение для использования в тестах
        yield app
        
        # После завершения тестов очищаем сессию и удаляем таблицы
        db.session.remove()
        db.drop_all()

# Фикстура для создания тестового клиента
@pytest.fixture
def client(app):
    return app.test_client()

# Фикстура для создания авторизационных заголовков с JWT токеном
@pytest.fixture
def auth_headers(app):
    with app.app_context():
        # Создаем тестовый JWT токен
        access_token = create_access_token(identity='test_user')
        return {'Authorization': f'Bearer {access_token}'}

# Тест получения списка оборудования
def test_show_equipment(client, auth_headers):
    """Позитивный тест получения списка оборудования"""
    # Отправляем GET запрос на эндпоинт /api/equipment/
    response = client.get('/api/equipment/', headers=auth_headers)
    
    # Проверяем, что сервер вернул код 200 (OK)
    assert response.status_code == 200
    
    # Получаем и проверяем данные ответа
    data = response.get_json()
    assert isinstance(data, list)  # Ответ должен быть списком
    assert len(data) > 0  # Список не должен быть пустым
    assert data[0]['name'] == "Test Equipment"  # Проверяем имя оборудования

# Тест добавления оборудования с валидными данными
def test_add_equipment_valid(client, auth_headers):
    """Позитивный тест добавления оборудования"""
    # Подготавливаем данные для отправки
    data = {'name': 'New Equipment'}
    
    # Отправляем POST запрос на добавление оборудования
    response = client.post('/api/equipment/add', 
                         json=data,
                         headers=auth_headers)
    
    # Проверяем ответ сервера
    assert response.status_code == 201  # Код 201 (Created)
    assert response.get_json()['name'] == 'New Equipment'  # Проверяем имя созданного оборудования

# Тест добавления оборудования без обязательного поля name
def test_add_equipment_missing_name(client, auth_headers):
    """Негативный тест - отсутствует обязательное поле name"""
    # Отправляем POST запрос с пустым телом
    response = client.post('/api/equipment/add', 
                         json={},
                         headers=auth_headers)
    
    # Проверяем, что сервер вернул ошибку 400 (Bad Request)
    assert response.status_code == 400
    assert 'error' in response.get_json()  # Ответ должен содержать поле error

# Тест добавления оборудования с дублирующимся именем
def test_add_equipment_duplicate_name(client, auth_headers):
    """Негативный тест - дублирование имени оборудования"""
    # Пытаемся создать оборудование с именем, которое уже существует
    data = {'name': 'Test Equipment'}
    response = client.post('/api/equipment/add', 
                         json=data,
                         headers=auth_headers)
    
    # Проверяем обработку ошибки
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['error']  # Проверяем текст ошибки

# Тест обновления оборудования с валидными данными
def test_update_equipment_valid(client, auth_headers):
    """Позитивный тест обновления оборудования"""
    # Получаем первое оборудование из базы данных
    equipment = Equipment.query.first()
    
    # Подготавливаем данные для обновления
    data = {'name': 'Updated Name'}
    
    # Отправляем PUT запрос на обновление оборудования
    response = client.put(f'/api/equipment/{equipment.id}', 
                        json=data,
                        headers=auth_headers)
    
    # Проверяем ответ сервера
    assert response.status_code == 200  # Код 200 (OK)
    assert response.get_json()['name'] == 'Updated Name'  # Проверяем обновленное имя

# Тест обновления оборудования с несуществующим ID
def test_update_equipment_invalid_id(client, auth_headers):
    """Негативный тест - несуществующий ID оборудования"""
    # Пытаемся обновить оборудование с несуществующим ID (9999)
    response = client.put('/api/equipment/9999', 
                        json={'name': 'Test'},
                        headers=auth_headers)
    
    # Проверяем, что сервер вернул 404 (Not Found)
    assert response.status_code == 404

# Тест удаления оборудования
def test_delete_equipment_valid(client, auth_headers):
    """Позитивный тест удаления оборудования"""
    # Получаем первое оборудование из базы данных
    equipment = Equipment.query.first()
    
    # Отправляем DELETE запрос на удаление оборудования
    response = client.delete(f'/api/equipment/{equipment.id}',
                           headers=auth_headers)
    
    # Проверяем ответ сервера
    assert response.status_code == 200  # Код 200 (OK)
    assert 'deleted' in response.get_json()['message']  # Проверяем сообщение об успешном удалении

# Тест попытки удаления оборудования с привязанными датчиками
def test_delete_equipment_with_sensors(client, auth_headers):
    """Негативный тест - удаление оборудования с привязанными датчиками"""
    # Получаем первое оборудование
    equipment = Equipment.query.first()
    
    # Создаем и привязываем датчик к этому оборудованию
    sensor = Sensor(name="Test Sensor", equipment_id=equipment.id)
    db.session.add(sensor)
    db.session.commit()
    
    # Пытаемся удалить оборудование с привязанным датчиком
    response = client.delete(f'/api/equipment/{equipment.id}',
                           headers=auth_headers)
    
    # Проверяем обработку ошибки
    assert response.status_code == 400  # Код 400 (Bad Request)
    assert 'referenced' in response.get_json()['error']  # Проверяем текст ошибки

# Тест добавления датчика к оборудованию с валидными данными
def test_add_sensor_to_equipment_valid(client, auth_headers):
    """Позитивный тест добавления датчика к оборудованию"""
    # Получаем первое оборудование
    equipment = Equipment.query.first()
    
    # Подготавливаем данные датчика
    data = {
        'name': 'New Sensor',
        'data_source': 'test_source',
        'sensor_type_id': 1
    }
    
    # Отправляем POST запрос на добавление датчика
    response = client.post(f'/api/equipment/{equipment.id}/sensors',
                         json=data,
                         headers=auth_headers)
    
    # Проверяем ответ сервера
    assert response.status_code == 201  # Код 201 (Created)
    assert response.get_json()['name'] == 'New Sensor'  # Проверяем имя созданного датчика

# Тест добавления датчика с неполными данными
def test_add_sensor_missing_fields(client, auth_headers):
    """Негативный тест - отсутствуют обязательные поля при добавлении датчика"""
    # Получаем первое оборудование
    equipment = Equipment.query.first()
    
    # Отправляем неполные данные датчика (только имя)
    data = {'name': 'Incomplete Sensor'}
    response = client.post(f'/api/equipment/{equipment.id}/sensors',
                         json=data,
                         headers=auth_headers)
    
    # Проверяем обработку ошибки
    assert response.status_code == 400  # Код 400 (Bad Request)