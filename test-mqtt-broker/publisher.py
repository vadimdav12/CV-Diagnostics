# import paho.mqtt.client as mqtt
# from thermal_sensor import get_device_thermal_sensor_data
# from current_sensor import get_device_current_sensor_data
# from vibration_sensor import get_device_vibration_sensor_data
#
# import time
# import json
#
# def on_connect(client, userdata, flags, reason_code, properties):
#     if reason_code == 0:
#         print("Подключено к брокеру!")
#     else:
#         print(f"Ошибка подключения: {reason_code}")
#
#
# def on_publish(client, userdata, mid, reason_code, properties):
#     print(f"Сообщение #{mid} доставлено")
#
# broker = "localhost"
# port = 1883
# username = None
# password = None
# topic = "telemetry"
#
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.on_connect = on_connect
# client.on_publish = on_publish
#
# try:
#     if username:
#         client.username_pw_set(username, password)
#
#     client.connect(broker, port, 60)
#     client.loop_start()
#
#     for i in range(1, 10):
#         #message = f"Тест #{i}"
#         message = get_device_thermal_sensor_data(1)
#         #result = client.publish(topic, message, qos=1)
#         # Публикация в MQTT
#         result = client.publish(topic=topic, payload=json.dumps(message), qos=1)
#
#         if result.rc == mqtt.MQTT_ERR_SUCCESS:
#             print(f"Отправлено: '{message}'")
#         else:
#             print(f"Ошибка отправки: {result.rc}")
#
#         time.sleep(1)
#
# except KeyboardInterrupt:
#     print("Прервано пользователем")
#
# finally:
#     client.loop_stop()
#     client.disconnect()
#     print("Отключение от брокера")
import json

import paho.mqtt.client as mqtt
import time

from current_sensor import get_device_current_sensor_data
from thermal_sensor import get_device_thermal_sensor_data


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Успешное подключение!")
        client.subscribe("test/topic")
    else:
        print(f"Ошибка подключения: {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = lambda c, u, m: print(f"Получено: {m.payload.decode()}")

try:
    client.connect("localhost", 1883, 60)
    client.loop_start()  # Фоновый поток для обработки сообщений
    mes_count = 0
    while True:
        message = get_device_current_sensor_data(1)
        #client.publish("sensor/1", "Ping!")
        # Публикация в MQTT
        result = client.publish(topic="sensor/1", payload=json.dumps(message), qos=1)
        # if result.rc == mqtt.MQTT_ERR_SUCCESS:
        #     print(f"Отправлено: '{message}'")
        # else:
        #     print(f"Ошибка отправки: {result.rc}")
        mes_count += 1
        if mes_count % 100 == 0:
            print(f"Отправлено {mes_count} сообщений")
        time.sleep(0.01)
except Exception as e:
    print(f"Ошибка: {e}")
finally:
    client.loop_stop()
    client.disconnect()