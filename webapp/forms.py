from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from webapp.models import User
import requests


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2, max=30)])
    nickname = StringField('Nickname', validators=[Length(min=2, max=20)])
    email = StringField('Email', validators=[Email()])
    steam_url = StringField('Steam profile URL', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    invite_code = StringField('Invite Code')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Use Login Instead')

    def validate_steam_url(self, steam_url):
        vanityurl = steam_url.data[30:]
        if vanityurl[-1] == '/':
            vanityurl=vanityurl[0:-1]
        steamid = steam_url.data[36:]
        if steamid[-1] == '/':
            steamid = steamid[0:-1]
        steam_response = requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='
                                      '8C75B9586976DFCAF894BD72AAC00538&vanityurl=' + vanityurl)
        steam_response_json = steam_response.json()
        if steam_response_json['response']['success'] != 1:
            steam_response =requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                          '?key=8C75B9586976DFCAF894BD72AAC00538&steamids=' + steamid)
            steam_response_json = steam_response.json()
            if steam_response_json['response']['players']:
                pass
            else:
                raise ValidationError('Incorrect steam profile URL')

    def validate_invite_code(self, invite_code):
        if invite_code.data != 'admin':
            invited_by = User.query.filter_by(invite_code=invite_code.data).first()
            print(invited_by.nickname)
            if invited_by:
                if int(invited_by.invites_left) <= 0:
                    raise ValidationError('Invite code expired!')
            else:
                raise ValidationError('Invalid invite code')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2, max=30)])
    nickname = StringField('Nickname', validators=[Length(min=2, max=20)])
    email = StringField('Email', validators=[Email()])
    steam_url = StringField('Steam Profile URL', validators=[DataRequired()])
    prev_username = StringField('username_prev')
    prev_email = StringField('email_prev')
    submit = SubmitField('Update')

    def validate_steam_url(self, steam_url):
        vanityurl = steam_url.data[30:]
        if vanityurl[-1] == '/':
            vanityurl = vanityurl[0:-1]
        steamid = steam_url.data[36:]
        if steamid[-1] == '/':
            steamid = steamid[0:-1]
        steam_response = requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='
                                      '8C75B9586976DFCAF894BD72AAC00538&vanityurl=' + vanityurl)
        steam_response_json = steam_response.json()
        if steam_response_json['response']['success'] != 1:
            steam_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                          '?key=8C75B9586976DFCAF894BD72AAC00538&steamids=' + steamid)
            steam_json = steam_response.json()
            print(steam_json)
            if steam_json['response']['players']:
                pass
            else:
                raise ValidationError('Incorrect steam profile URL')


class ChangePassword(FlaskForm):
    username = StringField('Username', validators=[Length(min=2, max=20)])
    password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Change')


class AddServer(FlaskForm):
    hostname = StringField('Hostname', validators=[Length(min=2, max=20)])
    location = SelectField('Server Location', default='BOM', choices=[('BOM', 'Mumbai'), ('PUNE', 'Pune')])
    ip = StringField('IP Address', validators=[DataRequired()])
    port = StringField('Port Number', validators=[DataRequired()])
    password = PasswordField('RCON Password', validators=[DataRequired()])
    submit = SubmitField('Add Server')
