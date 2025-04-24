# app/routes.py
from flask import Blueprint

from app.api import api_bp
from app.api.users import users_bp

main_bp = Blueprint('main', __name__)

# Дополнительные роуты
@main_bp.route('/')
def home():
    return "Главная страница"

# Регистрация всех API-роутов
def register_routes(app):
    # Основные Blueprint
    app.register_blueprint(main_bp)
    # API Blueprints
    app.register_blueprint(api_bp)  # автоматически включает все под-роуты

