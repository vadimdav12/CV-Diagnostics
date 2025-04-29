import json
import random
import time
from datetime import datetime

def get_device_current_sensor_data(device_id):
    # Формируем сообщение
    message = {
        "device": {
            "type": "PV-D9MG",
            "serial_number": f"PasserSN{device_id}",
            "timestamp": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
            "channel": device_id % 8 + 1  # Каналы от 1 до 8
        },
        "telemetry": generate_current_telemetry()
    }
    return message

def generate_current_telemetry():
    """Генерация параметров тока для станка"""
    base_current = random.uniform(4.0, 10.0)  # Базовый ток (А)
    return {
        # Базовые параметры
        "current_rms": round(base_current, 3),  # Среднеквадратичный ток
        "voltage_rms": round(random.uniform(380, 400), 1),  # Напряжение (В)
        "active_power": round(base_current * 380 * 0.85 / 1000, 2),  # Активная мощность (кВт)
        "reactive_power": round(base_current * 380 * 0.53 / 1000, 2),  # Реактивная мощность (кВАр)

        # Экстремальные значения
        "current_peak": round(base_current * 1.8, 3),  # Пиковый ток
        "current_min": round(base_current * 0.7, 3),  # Минимальный ток

        # Аналитические параметры
        "power_factor": round(random.uniform(0.82, 0.95)),  # Коэффициент мощности (cos φ)
        "thd_current": round(random.uniform(1.5, 8.0)), # Гармонические искажения тока (%)
        "unbalance": round(random.uniform(0.5, 5.0)), # Перекос фаз (%)

        # Диагностические метрики
        "inrush_current": round(base_current * 6.0, 1),          # Пусковой ток
        "overload_ratio": round(base_current / 8.0, 2),          # Отношение тока к номиналу
        "crest_factor": round(random.uniform(1.5, 2.2))          # Фактор амплитуды
    }


# Пояснение параметров:
# Параметр	Описание	Типичные значения
# current_rms	Среднеквадратичный ток (А)	4.0–10.0 A
# voltage_rms	Напряжение сети (В)	380–400 В
# active_power	Потребляемая активная мощность (кВт)	1.5–5.0 кВт
# reactive_power	Реактивная мощность (кВАр)	1.0–3.5 кВАр
# current_peak	Максимальный мгновенный ток (А)	До 18.0 A (пусковые)
# power_factor	Коэффициент мощности (cos φ)	0.82–0.95
# thd_current	Гармонические искажения тока (%)	1.5–8.0%
# inrush_current	Пусковой ток (А)	До 60.0 A