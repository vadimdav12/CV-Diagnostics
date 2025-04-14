class Sensor:
    def __init__(self, name, value=None, status=None, last_updated=None, id_s, chastota_sec=1, count_of_data=3 ):
        self.name = name
        self.id_s = id_s
        self.status = status
        self.last_updated = last_updated
        self.value = value
        self.count_of_data = count_of_data # число данных отправленных
        self.chastota = chastota # частота отправки данных


    def get_value(self):
        """Получить текущее значение  датчика"""
        return self.value()

    def get_status(self):
        """Получить текущее состояние  датчика"""
        status_info = {'name': self.name, 'data': self.data, 'location': self.location, 'status': self.status,
                       'last_updated': self.last_updated, 'battery_level': self.battery_level,
                       'connection_type': self.connection_type}
        return status_info

    def __str__(self):
        return f"Имя датчика: {self.name}, Последняя проверка:{self.last_updated}, статус: {self.status}, уровень батареи: {self.battery_level}, тип соединения {self.connection_type} "

    def __repr__(self):
        return f"Sensor({self.name}, {self.value}, {self.location}, {self.last_updated}, {self.battery_level}"


class ThermalSensor(Sensor):
    def __init__(self, value=None, location=None, status=None, last_updated=None, battery_level=None, connection_type=None):
        super().__init__("Температурный датчик", value, location, status, last_updated, battery_level, connection_type)



class ElectricSensor(Sensor):
    def __init__(self, value=None, location=None, status=None, last_updated=None, battery_level=None, connection_type=None):
        super().__init__("Электрический датчик", value, location, status, last_updated, battery_level, connection_type)


class VibrationSensor(Sensor):
    def __init__(self, value=None, location=None, status=None, last_updated=None, battery_level=None, connection_type=None):
        super().__init__("Вибрационный датчик", value, location, status, last_updated, battery_level, connection_type)