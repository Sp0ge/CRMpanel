from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    email = db.Column(db.String(40), index=True, unique=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    privilege = db.Column(db.String())
    join_date = db.Column(db.String())

class Privileges(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    privilege = db.Column(db.String(19), index=True, unique=True)

class System_files_patches(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pool_name = db.Column(db.String(60), index=True, unique=True)
    path = db.Column(db.String(254), index=True)

class Server_rules(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, unique=True)
    rule = db.Column(db.String(254), index=True)

class UsersFilesAccess(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    path = db.Column(db.String, unique=True, index=True)
    owner = db.Column(db.String, index=True)
    can_use = db.Column(db.String, index=True)
    magic_type = db.Column(db.String, index=True)

