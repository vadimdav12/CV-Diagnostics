import time
from datetime import datetime
import json
import random

def get_device_thermal_sensor_data(device_id):
    # Формируем сообщение
    message = {
        "device": {
            "type": "PV-D9MG",
            "serial_number": f"PasserSN{device_id}",
            "timestamp": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
            "channel": device_id % 8 + 1  # Каналы от 1 до 8
        },
        "telemetry": generate_temperature_telemetry()
    }
    return message

def generate_temperature_telemetry():
    """Генерация температурных телеметрических данных"""
    base_temp = random.uniform(20.0, 40.0)  # Базовая температура в °C
    return {
        "sensor_status": random.randint(0, 1),
        "temperature_current": round(base_temp, 2),
        "temperature_average": round(base_temp * random.uniform(0.95, 1.05), 2),
        "temperature_max": round(base_temp * 1.15, 2),
        "temperature_min": round(base_temp * 0.85, 2),
        "temperature_delta": round(random.uniform(0.1, 2.5), 2),
        "temperature_rate_change": round(random.uniform(-0.5, 0.5), 3),  # °C/сек
        "thermal_resistance": round(random.uniform(0.8, 1.2), 4),  # K/W
        "heat_flux": round(random.uniform(50, 200), 1),  # W/m²
        "thermal_derating": random.randint(0, 10),  # % снижения мощности
        "sensor_accuracy": round(random.uniform(0.1, 1.0), 2),  # ±°C
        "sensor_response_time": round(random.uniform(0.5, 5.0), 2)  # секунды
    }


# Параметр	Описание	Типичный диапазон
# sensor_status	Состояние датчика (1=работает, 0=ошибка)	0 или 1
# temperature_current	Текущая температура (°C)	20.0-40.0
# temperature_average	Средняя температура за период (°C)	±5% от current
# temperature_max	Максимальная зафиксированная (°C)	+15% от current
# temperature_min	Минимальная зафиксированная (°C)	-15% от current
# temperature_delta	Размах колебаний (°C)	0.1-2.5
# temperature_rate_change	Скорость изменения (°C/сек)	-0.5 до +0.5
# thermal_resistance	Термосопротивление (K/W)	0.8-1.2
# heat_flux	Тепловой поток (W/m²)	50-200
# thermal_derating	Снижение мощности из-за нагрева (%)	0-10%
# sensor_accuracy	Точность датчика (±°C)	0.1-1.0
# sensor_response_time	Время отклика (сек)	0.5-5.0