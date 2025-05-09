import pytest
from app import create_app, db
from app.models.sensor_type import Sensor_type
from app.models.sensor import Sensor
from flask_jwt_extended import create_access_token

# Фикстура для создания тестового приложения с конфигурацией 'testing'
@pytest.fixture
def app():
    app = create_app('testing')  # Создание экземпляра Flask-приложения с тестовой конфигурацией
    with app.app_context():
        db.create_all()  # Создание всех таблиц в тестовой базе данных

        # Добавление одного тестового типа датчика в БД
        st = Sensor_type(name="Test Sensor Type")
        db.session.add(st)
        db.session.commit()

        yield app  # Передача приложения в тесты

        # Очистка БД после завершения тестов
        db.session.remove()
        db.drop_all()

# Фикстура для клиента Flask, с помощью которого делаются HTTP-запросы к тестовому приложению
@pytest.fixture
def client(app):
    return app.test_client()

# Фикстура для генерации заголовков авторизации с JWT-токеном
@pytest.fixture
def auth_headers(app):
    with app.app_context():
        access_token = create_access_token(identity='test_user')  # Генерация токена для тестового пользователя
        return {'Authorization': f'Bearer {access_token}'}  # Формирование заголовков


def test_show_sensor_types(client):
    """Позитивный тест получения списка всех типов датчиков"""
    response = client.get('/sensor-type/')
    assert response.status_code == 200  # Ожидаем успешный ответ
    data = response.get_json()
    assert isinstance(data, list)  # Ответ должен быть списком
    assert len(data) > 0  # В списке должен быть хотя бы один элемент
    assert data[0]['name'] == "Test Sensor Type"  # Проверяем, что добавленный тип присутствует

def test_add_sensor_type_valid(client):
    """Позитивный тест добавления нового типа датчика"""
    data = {'name': 'New Sensor Type'}
    response = client.post('/sensor-type/add', json=data)
    assert response.status_code == 201  # Код 201 — успешно создано
    response_data = response.get_json()
    assert response_data['name'] == 'New Sensor Type'
    assert 'id' in response_data  # Новый объект должен содержать ID


def test_add_sensor_type_missing_name(client):
    """Негативный тест — отсутствует обязательное поле 'name'"""
    response = client.post('/sensor-type/add', json={})
    assert response.status_code == 400  # Ожидаем ошибку из-за отсутствия обязательного поля
    assert 'error' in response.get_json()
    assert 'required' in response.get_json()['error']  # Убедимся, что сообщение содержит слово "required"

def test_add_sensor_type_duplicate(client):
    """Негативный тест — попытка создать тип с уже существующим именем"""
    data = {'name': 'Test Sensor Type'}
    response = client.post('/sensor-type/add', json=data)
    assert response.status_code == 400  # Ошибка из-за дублирования имени
    assert 'already exists' in response.get_json()['error']

def test_update_sensor_type_valid(client):
    """Позитивный тест — обновление существующего типа датчика"""
    sensor_type = Sensor_type.query.first()
    data = {'name': 'Updated Sensor Type'}
    response = client.put(f'/sensor-type/{sensor_type.id}', json=data)
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Updated Sensor Type'

def test_update_sensor_type_invalid_id(client):
    """Негативный тест — попытка обновления несуществующего типа по ID"""
    response = client.put('/sensor-type/9999', json={'name': 'Test'})
    assert response.status_code == 404  # Ожидаем "Not Found"

def test_update_sensor_type_duplicate_name(client):
    """Негативный тест — обновление с именем, которое уже используется другим типом"""
    # Создаем второй тип датчика с другим именем
    st2 = Sensor_type(name="Another Type")
    db.session.add(st2)
    db.session.commit()

    # Пытаемся изменить первый тип датчика, присвоив ему имя второго
    sensor_type = Sensor_type.query.first()
    response = client.put(f'/sensor-type/{sensor_type.id}', json={'name': 'Another Type'})
    assert response.status_code == 400
    assert 'already exists' in response.get_json()['error']

def test_delete_sensor_type_valid(client):
    """Позитивный тест — удаление типа датчика без зависимостей"""
    sensor_type = Sensor_type.query.first()
    response = client.delete(f'/sensor-type/{sensor_type.id}')
    assert response.status_code == 200
    assert 'successfully' in response.get_json()['message']  # Проверка успешного удаления

def test_delete_sensor_type_with_sensors(client):
    """Негативный тест — попытка удаления типа, у которого есть связанные датчики"""
    sensor_type = Sensor_type.query.first()
    # Создаем датчик, связанный с этим типом
    sensor = Sensor(name="Test Sensor", sensor_type_id=sensor_type.id)
    db.session.add(sensor)
    db.session.commit()

    response = client.delete(f'/sensor-type/{sensor_type.id}')
    assert response.status_code == 400  # Ошибка из-за наличия зависимых записей
    assert 'referenced' in response.get_json()['error']
    assert 'sensors' in response.get_json()['error']

def test_delete_nonexistent_sensor_type(client):
    """Негативный тест — попытка удалить несуществующий тип датчика"""
    response = client.delete('/sensor-type/9999')
    assert response.status_code == 404  # Тип с таким ID не существует
