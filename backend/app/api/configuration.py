from flask import jsonify, Blueprint
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

configuration_bp = Blueprint('configuration', __name__)

# получить конфигурацию
@configuration_bp.route('/<user_id>', methods=['GET'])
def get_configuration(user_id):

    return jsonify({'message': 'configuration'}), 200

# добавление конфигурации
@configuration_bp.route('/<user_id>', methods=['POST'])
def add_configuration(user_id):

    return jsonify({'message': 'configuration'}), 200

# Изменение конфигурации
@configuration_bp.route('/<user_id>', methods=['PUT'])
def update_configuration(user_id):
    return jsonify({'message': 'configuration'}), 200


# Удаление конфигурации
@configuration_bp.route('/<user_id>', methods=['DELETE'])
def delete_configuration(user_id):
    return jsonify({'message': 'configuration'}), 200
