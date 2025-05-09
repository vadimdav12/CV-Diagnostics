import pytest
from app import create_app, db as _db  # Импортируем фабрику приложения и объект базы данных
from flask_jwt_extended import create_access_token  # Для создания JWT токена
from app.models.users import User, Role  # Модель пользователя и роли
from werkzeug.security import generate_password_hash  # Для безопасного хеширования пароля

# Фикстура для создания экземпляра приложения Flask с конфигурацией для тестирования
@pytest.fixture
def app():
    # Создаем приложение с тестовой конфигурацией ('testing' должна быть определена в конфигурациях приложения)
    app = create_app('testing')  
    
    # Входим в контекст приложения (нужно для работы с базой данных и другими объектами приложения)
    with app.app_context():
        _db.create_all()  # Создаем все таблицы в тестовой БД
        yield app         # Возвращаем объект приложения для использования в тестах
        _db.drop_all()    # Удаляем все таблицы после завершения тестов (чистка БД)

# Фикстура для клиента Flask, который используется для выполнения HTTP-запросов в тестах
@pytest.fixture
def client(app):
    return app.test_client()  # Возвращает тестовый клиент Flask

# Фикстура для доступа к объекту базы данных
@pytest.fixture
def db(app):
    return _db  # Возвращаем объект базы данных (используется в других фикстурах и тестах)

# Фикстура для генерации JWT токена для аутентифицированного пользователя
@pytest.fixture
def access_token(app, db):
    # Создаем тестового пользователя и роль
    user = User(
        username="testadmin", 
        email="test@example.com", 
        password_hash=generate_password_hash("password")  # Хешируем пароль
    )
    role = Role(name="admin")

    # Добавляем роль в БД и сохраняем
    db.session.add(role)
    db.session.commit()

    # Привязываем роль к пользователю
    user.roles.append(role)
    db.session.add(user)
    db.session.commit()

    # Создаем токен доступа внутри запроса (контекста), так как JWT требует контекста запроса
    with app.test_request_context():
        token = create_access_token(
            identity=str(user.id),  # Уникальный идентификатор пользователя
            additional_claims={"role": [r.name for r in user.roles]}  # Добавляем роль пользователя в токен
        )
        return token  # Возвращаем токен, который можно использовать для доступа к защищенным маршрутам
