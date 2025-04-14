import random
from sensor_models import ThermalSensor, VibrationSensor, ElectricSensor, Sensor
from sensors_data import sensors

def get_random_sensor_value(type_sensor):
    """Получаем рандомные значения датчиков
    type_sensors:
        * thermal_sensors - тепловые датчики
        * electrical_sensors - электрические датчики
        * vibration_sensors - вибрационные датчики
    """
    values = {}
    for param, diapason in sensors[type_sensor].items():
        min_ = diapason["min"]
        max_ = diapason["max"]
        value = random.choice([x for x in range(min_, max_ + 1)])
        values[param] = value

    return values
s = get_random_sensor_value("thermal_sensors")
therm_sensor1 = ThermalSensor(value=s)
print(repr(therm_sensor1))
# sensor = ThermalSensor()
