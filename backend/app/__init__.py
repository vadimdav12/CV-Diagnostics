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
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    # Конфигурация MQTT
    app.config['MQTT_BROKER_URL'] = 'localhost'
    app.config['MQTT_BROKER_PORT'] = 1883
    # Минимальная конфигурация кэша (используем простой встроенный кэш)
    app.config["CACHE_TYPE"] = "SimpleCache"
    # @mqtt.on_message()
    # def handle_message(client, userdata, message):
    #     from app.models.sensor_parameter import Sensor_parameter
    #     from app.models.sensor import Sensor
    #     from app.models.sensor_record import Sensor_Record
    #
    #     data = dict(
    #         topic=message.topic,
    #         payload=message.payload.decode())
    #
    #     with current_app.app_context():
    #         try:
    #             sensor = Sensor.query.filter_by(data_source=data['topic']).first()
    #             query = Sensor_parameter.query.filter(Sensor_parameter.sensor_id == sensor.id)
    #
    #             data_keys = query.with_entities(Sensor_parameter.key, Sensor_parameter.parameter_id).distinct().all()
    #
    #             payload = json.loads(data['payload'])
    #             # Пакетное добавление записей
    #             records = []
    #             for key in data_keys:
    #                 date_time = datetime.strptime(payload['device']['timestamp'], '%Y-%m-%d-%H:%M:%S')
    #                 records.append(Sensor_Record(sensor_id=sensor.id,timestamp=date_time,
    #                                   value=payload['telemetry'][key.key], parameter_id=key.parameter_id))
    #
    #             db.session.bulk_save_objects(records)
    #             db.session.commit()
    #             app.logger.info(f"Saved {len(records)} records for topic {data['topic']}")
    #             app.logger.info(f"Data saved for topic {data['topic']}")
    #         except Exception as e:
    #             db.session.rollback()
    #             app.logger.error(f"Database error: {str(e)}")

    def init_mqtt():
        # Привязываем MQTT к приложению
        mqtt.init_app(app)
    # Инициализация расширений
    db.init_app(app)
    cache.init_app(app)
    init_mqtt()
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

    # Создание базы и первичных данных
    with app.app_context():
        db.drop_all()
        db.create_all()
        # удаление данных таблиц
        Role.query.delete()
        User.query.delete()
        db.session.commit()
        create_roles_and_users()
        create_sensors_and_equipment()
        connect_to_topics()
        insert_bulk_data()

    # Регистрация всех маршрутов
    from app.routes import register_routes
    register_routes(app)

    from app.services import mqtt_service
    # Передаем app в mqtt_service
    mqtt_service.init_app(app)

    return app

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
    Sensor.query.delete()
    Sensor_Record.query.delete()
    Sensor_parameter.query.delete()
    Sensor_type.query.delete()
    Parameter.query.delete()
    Equipment.query.delete()
    db.session.commit()

    # Добавление тестовых данных
    types = ["тепловой", "вибрационный", "токовый"]
    for i in types:
        new_type = Sensor_type(name=i)
        db.session.add(new_type)

    n_q = Equipment(name="RS344")
    db.session.add(n_q)
    parameters = [["Пусковой ток", "Напряжение", "Гармонические искажения тока"],
                  ["СКЗ ускорения", "Смещение", "Доминирующая частота"],
                  ["Текущая температура", "Скорость изменения", "Средняя температура за период"]]
    units = [["A", "B", "%"], ["mm/s", "мкм", "Hz"], ["°C", "°C/сек", "°C"]]
    for p in range(len(parameters)):
        for i in range(len(parameters[p])):
            n_p = Parameter(name=parameters[p][i], unit=units[p][i])
            db.session.add(n_p)
    db.session.commit()
    sensor_types = [1, 2, 3]
    for i in sensor_types:
        name = f"D{i}"
        n_s = Sensor(name=name, data_source=f"sensor/{i}", sensor_type_id=i, equipment=n_q)
        db.session.add(n_s)
    db.session.commit()
    sensor_ids = [1, 2, 3]
    keys = ["inrush_current", "voltage_rms", "thd_current", "acceleration_rms", "displacement_rms", "dominant_frequency"
        , "temperature_current", "temperature_rate_change", "temperature_average"]
    for i in sensor_ids:
        s_p = Sensor_parameter(sensor_id=i, parameter_id=i, key=f"{keys[(i - 1) * 3]}")
        db.session.add(s_p)
    db.session.commit()

    print("Sensors and Equipment created successfully!")

def insert_bulk_data():
    from app.models.parameter import Parameter
    from app.models.sensor import Sensor
    from app.models.sensor_record import Sensor_Record

    sensor_ids = [1, 2, 3]            # ID датчиков
    parameter_ids = [1, 2, 3]               # ID параметров (например: температура, влажность, давление)
    print(datetime.now(timezone.utc))
    batch = []
    for _ in range(50):
        data = Sensor_Record(
            timestamp=datetime.now(timezone.utc),
            value=round(random.uniform(0, 100), 2),
            sensor_id=random.choice(sensor_ids),
            parameter_id=random.choice(parameter_ids))
        batch.append(data)

    # Вставляем весь список сразу одной транзакцией
    db.session.bulk_save_objects(batch)
    db.session.commit()

    print("Inserted 5000 rows in bulk!")

def connect_to_topics():
    from app.models.sensor import Sensor

    # Базовый запрос
    query = Sensor.query
    data_sources = [result.data_source for result in query.with_entities(Sensor.data_source).distinct().all()]
    print(data_sources)
    for source in data_sources:
        mqtt.subscribe(source)