import json
from threading import Lock
from collections import defaultdict
from datetime import datetime

from app import db, mqtt, cache

from app.models.sensor_record import Sensor_Record
from app.models.sensor_parameter import Sensor_parameter
from app.models.sensor import Sensor
# Настройки буферизации
BUFFER_MAX_SIZE = 1000  # Максимальный размер буфера перед записью
BUFFER_FLUSH_INTERVAL = 10  # Секунд между записями (если буфер не заполнен)

app = None  # Глобальная переменная

def init_app(flask_app):
    global app
    app = flask_app
    connect_to_topics()

class MQTT_Buffer:
    def __init__(self):
        self.buffer = defaultdict(list)
        self.lock = Lock()
        self.last_flush_time = datetime.now()

    def add_to_buffer(self, topic, records):
        with self.lock:
            self.buffer[topic].extend(records)
            if self.should_flush():
                self.flush_buffer()


    def should_flush(self):
        buffer_size = sum(len(records) for records in self.buffer.values())
        time_since_flush = (datetime.now() - self.last_flush_time).total_seconds()
        return buffer_size >= BUFFER_MAX_SIZE or time_since_flush >= BUFFER_FLUSH_INTERVAL

    def flush_buffer(self):
        try:
            all_records = []
            for topic, records in self.buffer.items():
                all_records.extend(records)

            if all_records:

                with app.app_context():
                    db.session.bulk_save_objects(all_records)
                    db.session.commit()
                    print(f"Flushed {len(all_records)} records to DB")

            self.buffer.clear()
            self.last_flush_time = datetime.now()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to flush buffer: {e}")

mqtt_buffer = MQTT_Buffer()

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("MQTT Connected")


@mqtt.on_message()
def handle_message(client, userdata, message):
    with app.app_context():
        try:
            topic = message.topic
            payload = json.loads(message.payload.decode())

            # Получаем sensor_id и параметры из кэша/БД
            sensor_id, data_keys = get_sensor_and_params(topic)
            if not sensor_id:
                return

            # Формируем записи для буфера
            records = []
            timestamp = datetime.strptime(payload['device']['timestamp'], '%Y-%m-%d-%H:%M:%S')
            for key in data_keys:
                records.append(Sensor_Record(
                    sensor_id=sensor_id,
                    parameter_id=key.parameter_id,
                    value=payload['telemetry'][key.key],
                    timestamp=timestamp
                ))

            # Добавляем в буфер
            mqtt_buffer.add_to_buffer(topic, records)

        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
        except Exception as e:
            print(f"MQTT Handler Error: {e}")


def get_sensor_and_params(topic):

    # Кэшируем данные, чтобы не дергать БД каждый раз
    cache_key = f"sensor_params_{topic}"
    cached = cache.get(cache_key)

    if cached:
        return cached["sensor_id"], cached["data_keys"]
    with app.app_context():
        sensor = Sensor.query.filter_by(data_source=topic).first()
        if not sensor:
            return None, None
        query = Sensor_parameter.query.filter(Sensor_parameter.sensor_id == sensor.id)
        data_keys = query.with_entities(Sensor_parameter.key, Sensor_parameter.parameter_id).distinct().all()

    cache.set(cache_key, {"sensor_id": sensor.id, "data_keys": data_keys}, timeout=3600)
    return sensor.id, data_keys

def connect_to_topics():
    from app.models.sensor import Sensor

    with app.app_context():
        # Базовый запрос
        query = Sensor.query
        data_sources = [result.data_source for result in query.with_entities(Sensor.data_source).distinct().all()]
        print(data_sources)
        for source in data_sources:
            mqtt.subscribe(source)
