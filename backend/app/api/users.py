from datetime import timedelta
import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, user_datastore
from ..models.users import Role, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/roles/')
def show_roles():
    roles = Role.query.all()
    return jsonify([{'id': role.id, 'name': role.name} for role in roles])

@users_bp.route('/', methods=['GET', 'OPTIONS'])
def show_users():
    if request.method == 'OPTIONS':
        return '', 200

    users = User.query.all()
    return jsonify([
        {'id': user.id, 'login': user.username, 'password': user.password_hash,
         'email': user.email, 'role': [i.name for i in user.roles]}
        for user in users
    ])

@users_bp.route('/protected', methods=['GET', 'OPTIONS'])
@jwt_required()
def protected():
    if request.method == 'OPTIONS':
        return '', 200

    user_id = get_jwt_identity()
    return jsonify(logged_in_as=user_id), 200

@users_bp.route('/add', methods=['POST', 'OPTIONS'])
def add_user():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email and password are required'}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Username or email already exists'}), 400

    username = data['username']
    password = data['password']
    new_user = User(username=username, email=data['email'], password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    role_name = data.get('role')
    if role_name:
        role = user_datastore.find_role(role_name)
        user_datastore.add_role_to_user(new_user, role)
        db.session.commit()

    return jsonify(new_user.to_dict()), 201

@users_bp.route('/<user_id>', methods=['PUT', 'OPTIONS'])
def update_user(user_id):
    if request.method == 'OPTIONS':
        return '', 200

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

@users_bp.route('/<user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    if request.method == 'OPTIONS':
        return '', 200

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@users_bp.route('/token', methods=['POST', 'OPTIONS'])
def token():
    if request.method == 'OPTIONS':
        return '', 200

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_datastore.find_user(username=username)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Could not verify'}), 401

    additional_claims = {"role": [i.name for i in user.roles]}
    expires = timedelta(minutes=120)
    access_token = create_access_token(identity=user.id, expires_delta=expires, additional_claims=additional_claims)
    return jsonify(access_token=access_token, role=additional_claims['role'], user_id=user.id), 200
