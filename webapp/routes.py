from flask import render_template, url_for, flash, redirect, request
from webapp import application, bcrypt, db
from webapp.models import User, Servers, Match, Matching
from webapp.steamapi import SteamAPI
from webapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, ChangePassword, AddServer
from secrets import token_hex
from flask_login import login_user, current_user, logout_user, login_required, login_manager


@application.errorhandler(404)
def page_not_found(e):
    if current_user.is_authenticated:
        return render_template('error.html', error=e, email=current_user.email, title='Page Not Found', user=current_user)
    return render_template('error.html', error=e, title='Page Not found', user=False)


@application.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', email=current_user.email, index=1, user=current_user)
    return render_template('index.html', index=1, user=False)


@application.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(next_url) if next_url else redirect(url_for('index'))
        else:
            flash("Incorrect email or password", "danger")
    return render_template('login.html', title='Login', form=form, user=False)


@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        steam_api = SteamAPI()
        (steam_id, profile_pic, profile_url) = steam_api.steam_id_profile(form.steam_url.data)
        if form.invite_code.data == 'admin':
            user = User(name=form.name.data, nickname=form.nickname.data, email=form.email.data, password=hashed_pw,
                        steamid=steam_id, profile_url=profile_url, admin=True, moderator=False,
                        invite_code=token_hex(8), invited_by=99999, profile_pic=profile_pic)
        else:
            invited_by = User.query.filter_by(invite_code=form.invite_code.data).first()
            user = User(name=form.name.data, nickname=form.nickname.data, email=form.email.data, password=hashed_pw,
                        steamid=steam_id, profile_url=profile_url, admin=False, moderator=False,
                        invite_code=token_hex(8), invited_by=invited_by.id, profile_pic=profile_pic)
            invited_by.invites_left = invited_by.invites_left - 1
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, user=False)


@application.route('/servers', methods=['GET'])
@login_required
def servers():
    if current_user.admin:
        game_servers = Servers.query.filter_by(user_id=current_user.id).all()
        return render_template('servers.html', email=current_user.email, servers=game_servers, title='Servers', user=current_user)
    return redirect(url_for('unauth.html'))


@application.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        other_user = User.query.filter_by(email=form.email.data).first()
        if other_user:
            if other_user.id != current_user.id:
                flash('Email address already taken', 'warning')
                return redirect(url_for('account'))
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.nickname = form.nickname.data
        steam_api = SteamAPI()
        (steam_id, profile_pic, profile_url) = steam_api.steam_id_profile(form.steam_url.data)
        current_user.steamid = steam_id
        current_user.profile_url = profile_url
        current_user.profile_pic = profile_pic
        db.session.commit()
        flash("Account Information Updated Successfully!", "success")
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.nickname.data = current_user.nickname
        form.steam_url.data = current_user.profile_url
    return render_template('account.html', email=current_user.email, form=form, user=current_user, title='Account')


@application.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Password changed successfully', 'info')
            return redirect(url_for('account'))
        else:
            flash('Incorrect password!, Please try again.', 'danger')
            return redirect('changepassword')
    elif request.method == 'GET':
        form.username = current_user.nickname
    return render_template('change_password.html', form=form, email=current_user.email, user=current_user, title='Change Password')


@application.route('/logout')
def logout():
    current_user.searching = False
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@application.route('/forgot_password')
def forgot_password():
    logout_user()
    return render_template('forgot_password.html', user=False, title='Forgot Password')


@application.route('/add_server', methods=['GET', 'POSt'])
@application.route('/addserver', methods=['GET', 'POST'])
@login_required
def add_server():
    if current_user.admin:
        form = AddServer()
        if form.validate_on_submit():
            server = Servers(hostname=form.hostname.data, location=form.location.data, ip=form.ip.data,
                             password=form.password.data, user_id=current_user.id, port=form.port.data)
            db.session.add(server)
            db.session.commit()
            flash('Server added!', 'success')
            return redirect(url_for('servers'))
        return render_template('add_server.html', email=current_user.email, form=form, title='Add Server', user=current_user)
    return render_template('unauth.html', email=current_user.email, title='Unauthorised', user=current_user)


@application.route('/confirmdelete/<id>')
@login_required
def confirm_delete(id):
    server = Servers.query.filter_by(id=id).first()
    if server.user_id == current_user.id:
        return render_template('confirm_delete.html', email=current_user.email, user=current_user, title='Confirm Server Deletion', id=id)
    return redirect(url_for('server'))


@application.route('/delete/<id>')
@login_required
def delete(id):
    Servers.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('servers'))


@application.route('/play')
@login_required
def play():
    if current_user.playing:
        return redirect(url_for('matchpage'))
    current_user.searching = True
    db.session.commit()
    return render_template('play.html', email=current_user.email, title='Play', user=current_user, matchpage=True)


@application.route('/matchpage')
@login_required
def matchpage():
    if current_user.searching:
        return redirect(url_for('play'))
    if current_user.playing:
        all_players = Matching.query.filter_by(match_id=current_user.current_match_id).all()
        all_participants = []
        for player in all_players:
            participant = User.query.filter_by(id=player.user_id).first()
            all_participants.append(participant)
        return render_template('matchpage.html', email=current_user.email, title='Match Room', user=current_user,
                               all_participants=all_participants, matchpage=True)
    return redirect(url_for('index'))


@application.route('/users')
@login_required
def users():
    if current_user.admin:
        all_users = User.query.all()
        return render_template('users.html', email=current_user.email, user=current_user, all_users=all_users,
                               title='All Users')
    return redirect(url_for('index'))
