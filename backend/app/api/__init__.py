from flask import Blueprint
# Импорт всех под-роутов
from .users import users_bp
from .sensors import sensors_bp
from .sensor_types import sensor_type_bp
from .equipment import equipment_bp

# Создание главного Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')
# Регистрируем users_bp внутри api_bp
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(sensors_bp, url_prefix='/sensors')
api_bp.register_blueprint(sensor_type_bp, url_prefix='/sensor-type')
api_bp.register_blueprint(equipment_bp, url_prefix='/equipment')