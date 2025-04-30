import json
import random
import time
from datetime import datetime

def get_device_vibration_sensor_data(device_id):
    # Формируем сообщение
    message = {
        "device": {
            "type": "PV-D9MG",
            "serial_number": f"PasserSN{device_id}",
            "timestamp": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
            "channel": device_id % 8 + 1  # Каналы от 1 до 8
        },
        "telemetry": generate_vibration_telemetry()
    }
    return message

def generate_vibration_telemetry():
    """Генерация вибропараметров для станка"""
    base_vib = random.uniform(0.1, 2.0)  # Базовый уровень вибрации (mm/s)
    return {
        # Основные параметры
        "vibration_rms": round(base_vib, 4),  # Среднеквадратичное значение (mm/s)
        "acceleration_rms": round(base_vib * 0.5, 4),  # СКЗ ускорения (g)
        "displacement_rms": round(base_vib * 50, 2),  # Смещение (мкм)

        # Пиковые значения
        "vibration_peak": round(base_vib * 2.5, 4),  # Пиковая вибрация (mm/s)
        "acceleration_peak": round(base_vib * 3.0, 4),  # Макс. ускорение (g)

        # Частотные характеристики
        "dominant_frequency": round(random.uniform(10, 500)),  # Доминирующая частота (Hz)
        "harmonic_ratio": round(random.uniform(0.1, 0.5)),  # Уровень гармоник

        # Диагностические метрики
        "crest_factor": round(random.uniform(2.0, 5.0)),
        # Фактор амплитуды
        "kurtosis": round(random.uniform(2.0, 8.0)),  # Эксцесс (острота пиков)
        "unbalance_level": round(random.uniform(0.1, 1.5)),  # Уровень дисбаланса
    }