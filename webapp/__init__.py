from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_socketio import SocketIO
from flask_login import LoginManager
from secrets import token_hex
import os

application = Flask(__name__)
application.config['SECRET_KEY'] = token_hex(20)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
api = Api(application)
sock = SocketIO(application)
login_manager = LoginManager(application)


from webapp import routes
from webapp import socket
from webapp.myapi import MyApi

api.add_resource(MyApi, '/api/<string:serverid>')

if os.path.exists('webapp/site.db'):
    pass
else:
    db.create_all()
