# backend/tests/conftest.py
import pytest
from app import create_app, db as _db
from flask_jwt_extended import create_access_token
from app.models.users import User, Role
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app('testing')  # Убедись, что у тебя есть конфигурация для тестов
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return _db

@pytest.fixture
def access_token(app, db):
    user = User(username="testadmin", email="test@example.com", password_hash=generate_password_hash("password"))
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()
    user.roles.append(role)
    db.session.add(user)
    db.session.commit()

    with app.test_request_context():
        token = create_access_token(identity=str(user.id), additional_claims={"role": [r.name for r in user.roles]})
        return token
