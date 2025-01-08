from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user, login_required
from . import _db as db

# https://hackmd.io/@wMOj49BAS5KWi8DcomZLYw/piao

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    def __init__(self, name, email):
        self.name =name
        self.email = email

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gid = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80),  nullable=False)
    longitude = db.Column(db.String(80),  nullable=False)
    latitude = db.Column(db.String(80),  nullable=False)
    rating = db.Column(db.Float,  nullable=False)
    price_level = db.Column(db.Float,  nullable=False)

    def __init__(self, name, address):
        self.name =name
class OpenTime(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
from os.path import join, dirname
path = join(dirname(__file__), 'static')
ALL_ADMIN_VIEW = (FileAdmin('c:\\', name='File Manager', endpoint='/file_manager'),ModelView(Test,db.session, ModelView(Restaurant,db.session))) # 

