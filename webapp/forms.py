from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from webapp.models import User
from webapp.steamapi import SteamAPI
from flask_login import current_user


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
        steam_api = SteamAPI()
        (steam_id, profile_pic, profile_url) = steam_api.steam_id_profile(steam_url.data)
        if steam_id:
            pass
            # hours = steam_api.game_hours(steam_id)
            # if hours < 3393359:
            #     raise ValidationError('Insufficient experience in-game')
        else:
            raise ValidationError('Incorrect steam profile URL')

    def validate_invite_code(self, invite_code):
        if invite_code.data != 'admin':
            invited_by = User.query.filter_by(invite_code=invite_code.data).first()
            if invited_by:
                if invited_by.invites_left <= 0:
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

    def validate_email(self, email):
        other_user = User.query.filter_by(email=email.data).first()
        if other_user:
            if other_user.id != current_user.id:
                raise ValidationError('Email already used! Choose another one')

    def validate_steam_url(self, steam_url):
        steam_api = SteamAPI()
        (steam_id, profile_pic, profile_url) = steam_api.steam_id_profile(steam_url.data)
        if steam_id:
            pass
            # hours = steam_api.game_hours(steam_id)
            # if hours < 3393359:
            #     raise ValidationError('Insufficient experience in-game')
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
    location = SelectField('Server Location', default='BOM',
                           choices=[('BOM', 'Mumbai'), ('PUNE', 'Pune'), ('MAS', 'Madras')])
    ip = StringField('IP Address', validators=[DataRequired()])
    port = IntegerField('Port Number', validators=[DataRequired()])
    password = StringField('RCON Password', validators=[DataRequired()])
    submit = SubmitField('Add Server')

    def validate_port(self, port):
        if int(port.data) > 65536 or int(port.data) < 1:
            raise ValidationError('Incorrect port number')
