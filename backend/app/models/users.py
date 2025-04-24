# import UserMixin, RoleMixin
from flask import jsonify
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore

from app import db

roles_users = db.Table('roles_users',
                             db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                             db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True)
    # backreferences the user_id from roles_users table
    roles = db.relationship('Role', secondary=roles_users, backref='roles')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': [i.name for i in self.roles]
    }

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(80))
