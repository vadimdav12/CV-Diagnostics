from datetime import timedelta

from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

from werkzeug.security import check_password_hash, generate_password_hash
from ..services.decorators import has_roles

users_bp = Blueprint('users', __name__)

from ..models.users import Role, User
from app import db, user_datastore

@users_bp.route('/roles/', methods=['GET'])
#@jwt_required()
#@has_roles(allowed_roles=['admin'])
def show_roles():

    roles = Role.query.all()
    return jsonify([{'id': role.id, 'name': role.name} for role in roles])


@users_bp.route('/', methods=['GET'])
#@jwt_required()
#@has_roles(allowed_roles=['admin'])
def show_users():
    users = User.query.all()

    return jsonify([{'id': user.id, 'login': user.username,'password': user.password_hash,
                     'email': user.email,'role': [i.name for i in user.roles]} for user in users])

# Защищенный маршрут
@users_bp.route('/protected', methods=['GET'])
#@jwt_required()
def protected():
    user_id = get_jwt_identity()

    return jsonify(logged_in_as=user_id), 200


# Добавление пользователя
@users_bp.route('/add', methods=['POST'])
#@jwt_required()
#@has_roles(allowed_roles=['admin'])
def add_user():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username and email are required'}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Username or email already exists'}), 400

    username=data['username']
    password = data['password']

    new_user = User(username=username, email=data['email'], password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    role = data['role']
    user_datastore.add_role_to_user(user_datastore.find_user(username=username),  user_datastore.find_role(role))
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


# Изменение пользователя
@users_bp.route('/<user_id>', methods=['PUT'])
#@jwt_required()
#@has_roles(allowed_roles=['admin'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'username' in data:
        if data['username'] != user.username and User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']

    if 'email' in data:
        if data['email'] != user.email and User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']

    db.session.commit()
    return jsonify(user.to_dict()), 200


# Удаление пользователя
@users_bp.route('/<user_id>', methods=['DELETE'])
#@jwt_required()
#@has_roles(allowed_roles=['admin'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@users_bp.route('/token', methods =['POST'])
def token():

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        # returns 401 if any email or / and password is missing
        return 'Could not verify'

    user = user_datastore.find_user(username=username)
    if not user:
        return 'Could not verify', 401

    if check_password_hash(user.password_hash, password):
        # Создаем токен с дополнительными claims (ролью пользователя)
        additional_claims = {"role": [i.name for i in user.roles]}
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=120), additional_claims=additional_claims)
        return jsonify(access_token=access_token, role=additional_claims['role'], user_id=user.id), 200
    return 'Could not verify', 403