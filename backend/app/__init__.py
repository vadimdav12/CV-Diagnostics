import datetime
import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory, abort

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from  werkzeug.security import generate_password_hash, check_password_hash

from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

# Инициализация SQLAlchemy
db = SQLAlchemy()
# Переменная для user_datastore (будет инициализирована в create_app)
user_datastore = None

def create_app():
    global user_datastore  #user_datastore глобальной переменной

    # Загружаем переменные из файла .env
    load_dotenv()

    app = Flask(__name__, static_folder=None)
    CORS(app)  # Разрешить CORS для всех маршрутов

    # Конфигурация базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    app.config['JSON_AS_ASCII'] = os.getenv('JSON_AS_ASCII')
    app.config['JSON_SORT_KEYS'] = os.getenv('JSON_SORT_KEYS')
    # Настройка Flask-Security
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['SECURITY_JOIN_USER_ROLES'] = os.getenv('SECURITY_JOIN_USER_ROLES')
    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') # Секретный ключ для подписи токенов

    # Инициализация SQLAlchemy
    db.init_app(app)
    # Инициализация Flask-Migrate
    #migrate = Migrate(app, db)

    @app.route('/swagger_ui/<path:path>')
    def send_static(path):
        return send_from_directory('swagger_ui', path)

    # Конфигурация для Swagger UI
    SWAGGER_URL = '/swagger'  # URL для доступа к Swagger UI
    API_URL = '/swagger_ui/swagger.yml'

    # Создание Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Sample API"})

    # Регистрация Swagger UI blueprint в приложении
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    from app.models.users import Role
    from app.models.users import User
    # Создаем user_datastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    jwt = JWTManager(app)

    def create_roles():
        user_datastore.create_role(id=1, name='admin', description="Admin")
        user_datastore.create_role(id=3, name='user', description="User")

        user_datastore.create_user(username='admin', email='1@mail.ru',password_hash=generate_password_hash('admin'))
        user_datastore.create_user(username='manager', email='2@mail.ru', password_hash=generate_password_hash('manager'))
        user_datastore.create_user(username='user', email='3@mail.ru', password_hash=generate_password_hash('user'))
        db.session.commit()
        user = user_datastore.find_user(username='admin')
        admin_role = user_datastore.find_role('admin')

        user_datastore.add_role_to_user(user, admin_role)
        user_datastore.add_role_to_user(user_datastore.find_user(username='manager'), user_datastore.find_role('user'))
        user_datastore.add_role_to_user(user_datastore.find_user(username='user'), user_datastore.find_role('user'))
        db.session.commit()

        print("Roles created successfully!")

    def create_sensors():
        from app.models.sensor_type import Sensor_type
        from app.models.parameter import Parameter
        from app.models.sensor import Sensor
        from app.models.sensor_parameter import Sensor_parameter
        from app.models.sensor_record import Sensor_Record
        from app.models.equipment import Equipment

        db.drop_all()
        db.create_all()
        Sensor_type.query.delete()
        Parameter.query.delete()
        Sensor.query.delete()
        Sensor_parameter.query.delete()
        Sensor_Record.query.delete()
        Equipment.query.delete()
        db.session.commit()

        n_q = Equipment(name="RS344")
        db.session.add(n_q)
        new_type = Sensor_type(name="тепловой")
        db.session.add(new_type)
        n_p = Parameter(name="Смещение", unit="мкм")
        db.session.add(n_p)
        db.session.commit()
        n_s=Sensor(name="D1",data_source="d/1/t1/122", sensor_type=new_type,equipment=n_q)
        db.session.add(n_s)
        db.session.commit()
        s_p = Sensor_parameter(sensor=n_s, parameter=n_p)
        db.session.add(s_p)
        db.session.commit()
        with db.session.no_autoflush:
            t1 = Sensor_Record(timestamp=datetime.datetime.now(),value=0.11, sensor=n_s, parameter=n_p)
            db.session.add(t1)
        db.session.commit()


        r = Sensor_Record.query.all()
        for e in r:
            print(e.timestamp, e.value)
        #new_type = Parameter(name="тепловой")
    # Удаление и Создание базы данных и таблиц
    with app.app_context():
        db.drop_all()
        db.create_all()
        # удаление данных таблиц
        Role.query.delete()
        User.query.delete()

        db.session.commit()
        create_sensors()
        create_roles()

    from app.routes import register_routes
    # Регистрация всех роутов
    register_routes(app)

    return app