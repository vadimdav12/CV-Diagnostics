import time

from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import random

# Функция создания начальных данных для датчиков, параметров, оборудования и связи
#  датчиков и параметров
def create_sensors_and_equipment():
    from app import db
    from app.models.sensor_type import Sensor_type
    from app.models.parameter import Parameter
    from app.models.sensor import Sensor
    from app.models.sensor_parameter import Sensor_parameter
    from app.models.sensor_record import Sensor_Record
    from app.models.equipment import Equipment

    # Очистка и пересоздание таблиц
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
    types = ["токовый", "тепловой", "вибрационный"]
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
    keys = ["telemetry.inrush_current", "telemetry.voltage_rms", "telemetry.thd_current", "telemetry.acceleration_rms", "telemetry.displacement_rms", "telemetry.dominant_frequency"
        , "telemetry.temperature_current", "telemetry.temperature_rate_change", "telemetry.temperature_average"]
    for i in sensor_ids:
        s_p = Sensor_parameter(sensor_id=i, parameter_id=i, key=f"{keys[(i - 1) * 3]}")
        db.session.add(s_p)
    db.session.commit()

    print("Sensors and Equipment created successfully!")

# Функция создания начальных данных от датчиков
def insert_bulk_data(count):
    from app import db
    from app.models.sensor_record import Sensor_Record

    sensor_ids = [1, 2, 3]            # ID датчиков
    parameter_ids = [1, 2, 3]               # ID параметров (например: температура, влажность, давление)
    print(datetime.now(timezone.utc))
    batch = []
    for _ in range(count):
        data = Sensor_Record(
            timestamp=datetime.now(timezone.utc),
            value=round(random.uniform(0, 100), 2),
            sensor_id=random.choice(sensor_ids),
            parameter_id=random.choice(parameter_ids))
        time.sleep(0.1)
        batch.append(data)

    # Вставляем весь список сразу одной транзакцией
    db.session.bulk_save_objects(batch)
    db.session.commit()

    print(f"Inserted {count} rows in bulk!")

# Функция создания начальных данных для пользователей
def create_roles_and_users():
    from app import db, user_datastore

    user_datastore.create_role(id=1, name='admin', description="Admin")
    user_datastore.create_role(id=2, name='user', description="User")

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


def create_tables():
    from app import db
    from app.models.users import Role, User
    from app.models.sensor_type import Sensor_type
    from app.models.parameter import Parameter
    from app.models.sensor import Sensor
    from app.models.sensor_parameter import Sensor_parameter
    from app.models.sensor_record import Sensor_Record
    from app.models.equipment import Equipment
    from app.models.configuration import Configuration

    # Очистка и пересоздание таблиц
    db.drop_all()
    db.create_all()

    # Очистка данных
    Role.query.delete()
    User.query.delete()
    Sensor.query.delete()
    Sensor_Record.query.delete()
    Sensor_parameter.query.delete()
    Sensor_type.query.delete()
    Parameter.query.delete()
    Equipment.query.delete()
    Configuration.query.delete()
    db.session.commit()