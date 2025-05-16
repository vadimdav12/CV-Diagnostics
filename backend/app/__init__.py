import json
from datetime import datetime, timezone
import os
import random

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash

from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt
from flask_caching import Cache

from app.services.init_test_data import create_roles_and_users, create_sensors_and_equipment, insert_bulk_data, \
    create_tables

# Инициализация расширений
db = SQLAlchemy()
mqtt = Mqtt()
cache = Cache()
user_datastore = None

def create_app():
    global user_datastore  #user_datastore глобальной переменной

    # Загружаем переменные окружения
    load_dotenv()

    # Инициализация Flask
    app = Flask(__name__, instance_relative_config=True)

    CORS(app)  # Разрешить CORS для всех маршрутов

    # Конфигурация базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    # Настройка конфигурации из .env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    app.config['JSON_AS_ASCII'] = os.getenv('JSON_AS_ASCII', 'False') == 'True'
    app.config['JSON_SORT_KEYS'] = os.getenv('JSON_SORT_KEYS', 'False') == 'True'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['SECURITY_JOIN_USER_ROLES'] = os.getenv('SECURITY_JOIN_USER_ROLES', 'False') == 'True'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_IDENTITY_CLAIM'] = os.getenv('JWT_IDENTITY_CLAIM')
    app.config['MQTT_BROKER_URL'] = os.getenv('MQTT_BROKER_URL')
    app.config['MQTT_BROKER_PORT'] = int(os.getenv('MQTT_BROKER_PORT'))
    # Минимальная конфигурация кэша (используем простой встроенный кэш)
    app.config["CACHE_TYPE"] =  os.getenv('CACHE_TYPE')

    # Инициализация расширений
    db.init_app(app)
    cache.init_app(app)
    mqtt.init_app(app)
    jwt = JWTManager(app)

    # Swagger статические файлы
    @app.route('/swagger_ui/<path:path>')
    def send_static(path):
        return send_from_directory('swagger_ui', path)

    # Swagger UI конфигурация
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger_ui/swagger.yml'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "CV Diagnostics API"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Импорт моделей для Flask-Security
    from app.models.users import Role, User
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    with app.app_context():

        # удаление данных таблиц
        create_tables()

        # создание начальных данных
        create_roles_and_users()
        create_sensors_and_equipment()
        #insert_bulk_data(5000)

    # Регистрация всех маршрутов
    from app.routes import register_routes
    register_routes(app)

    from app.services import mqtt_service
    # Передаем app в mqtt_service
    mqtt_service.init_app(app)

    return app