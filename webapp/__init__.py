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
application.config['SERVER_URL'] = 'https://cargo.win'
application.config['STEAM_API_KEY'] = '<steam API Key>'
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
api_match_start = Api(application)
sock = SocketIO(application, cors_allowed_origins='*')
login_manager = LoginManager(application)


from webapp import routes, socket, status
from webapp.myapi import MyApiMatchStart

api_match_start.add_resource(MyApiMatchStart, '/api/match/<string:match_id>/<string:event>')

if os.path.exists('webapp/site.db'):
    pass
else:
    db.create_all()
