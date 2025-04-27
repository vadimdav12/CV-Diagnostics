import datetime
import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash

from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

# Инициализация расширений
db = SQLAlchemy()
user_datastore = None

def create_app():
    global user_datastore

    # Загружаем переменные окружения
    load_dotenv()

    # Инициализация Flask
    app = Flask(__name__, instance_relative_config=True)

    # Загружаем config.py
    app.config.from_pyfile('config.py', silent=True)

    # Разрешение CORS
    CORS(
        app,
        resources = {r"/api/*": {"origins": "http://localhost:3000"}},
        supports_credentials = True,
        allow_headers = ["Authorization", "Content-Type"],  # <— разрешаем эти заголовки
        expose_headers = ["Authorization"]  # <— если нужно читать заголовок ответа
                          )

    # Настройка конфигурации из .env или config.py
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') or app.config.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    app.config['JSON_AS_ASCII'] = os.getenv('JSON_AS_ASCII', 'False') == 'True'
    app.config['JSON_SORT_KEYS'] = os.getenv('JSON_SORT_KEYS', 'False') == 'True'

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or app.config.get('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT') or app.config.get('SECURITY_PASSWORD_SALT')
    app.config['SECURITY_JOIN_USER_ROLES'] = os.getenv('SECURITY_JOIN_USER_ROLES', 'False') == 'True'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or app.config.get('JWT_SECRET_KEY')
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'

    # Инициализация расширений
    db.init_app(app)
    jwt = JWTManager(app)

    # Swagger статические файлы
    @app.route('/swagger_ui/<path:path>')
    def send_static(path):
        return send_from_directory('swagger_ui', path)

    # Swagger UI конфигурация
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger_ui/swagger.yml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "CV Diagnostics API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Импорт моделей для Flask-Security
    from app.models.users import Role, User
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    # Функция создания начальных данных
    def create_roles_and_users():
        user_datastore.create_role(id=1, name='admin', description="Admin")
        user_datastore.create_role(id=3, name='user', description="User")

        user_datastore.create_user(username='admin', email='1@mail.ru', password_hash=generate_password_hash('admin'))
        user_datastore.create_user(username='manager', email='2@mail.ru', password_hash=generate_password_hash('manager'))
        user_datastore.create_user(username='user', email='3@mail.ru', password_hash=generate_password_hash('user'))
        db.session.commit()

        admin = user_datastore.find_user(username='admin')
        user_role = user_datastore.find_role('user')

        user_datastore.add_role_to_user(admin, user_datastore.find_role('admin'))
        user_datastore.add_role_to_user(user_datastore.find_user(username='manager'), user_role)
        user_datastore.add_role_to_user(user_datastore.find_user(username='user'), user_role)
        db.session.commit()

        print("Roles and Users created successfully!")

    def create_sensors_and_equipment():
        from app.models.sensor_type import Sensor_type
        from app.models.parameter import Parameter
        from app.models.sensor import Sensor
        from app.models.sensor_parameter import Sensor_parameter
        from app.models.sensor_record import Sensor_Record
        from app.models.equipment import Equipment

        # Очистка и пересоздание таблиц
        db.drop_all()
        db.create_all()

        # Очистка данных
        Sensor_type.query.delete()
        Parameter.query.delete()
        Sensor.query.delete()
        Sensor_parameter.query.delete()
        Sensor_Record.query.delete()
        Equipment.query.delete()
        db.session.commit()

        # Добавление тестовых данных
        equipment = Equipment(name="RS344")
        db.session.add(equipment)

        sensor_type = Sensor_type(name="тепловой")
        db.session.add(sensor_type)

        parameter = Parameter(name="Смещение", unit="мкм")
        db.session.add(parameter)

        db.session.commit()

        sensor = Sensor(name="D1", data_source="d/1/t1/122", sensor_type=sensor_type, equipment=equipment)
        db.session.add(sensor)
        db.session.commit()

        sensor_param = Sensor_parameter(sensor=sensor, parameter=parameter)
        db.session.add(sensor_param)
        db.session.commit()

        record = Sensor_Record(timestamp=datetime.datetime.now(), value=0.11, sensor=sensor, parameter=parameter)
        db.session.add(record)
        db.session.commit()

        print("Sensors and Equipment created successfully!")

    # Создание базы и первичных данных
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_sensors_and_equipment()
        create_roles_and_users()

    # Регистрация всех маршрутов
    from app.routes import register_routes
    register_routes(app)

    return app
