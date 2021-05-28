from flask import render_template, url_for, flash, redirect, request, make_response
from webapp import application, bcrypt, db
from webapp.models import User, Servers
from webapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, ChangePassword, AddServer
import requests
from secrets import token_hex


@application.errorhandler(404)
def page_not_found(e):
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('error.html', error=e, email=email, title='Page Not Found', user=user)
        return redirect(url_for('logout', next=request.endpoint))
    return render_template('error.html', error=e, title='Page Not found', user=False)


@application.route('/')
def index():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('index.html', email=email, index=1, user=user)
        return redirect(url_for('logout'))
    return render_template('index.html', index=1, user=False)


@application.route('/login', methods=['GET', 'POST'])
def login():
    email = request.cookies.get('email')
    next_url = request.form.get("next")
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect(url_for('index'))
        return redirect(url_for('logout'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if next_url:
                resp = make_response(redirect(url_for(next_url)))
                resp.set_cookie('email', form.email.data)
                return resp
            resp = make_response(redirect('/'))
            resp.set_cookie('email', form.email.data)
            return resp
        else:
            flash("Incorrect nickname or password", "danger")
    return render_template('login.html', title='Login', form=form, user=False)


@application.route('/register', methods=['GET', 'POST'])
def register():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            return redirect(url_for('index'))
        return redirect(url_for('logout'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        vanityurl = form.steam_url.data[30:]
        if vanityurl[-1] == '/':
            vanityurl = vanityurl[0:-1]
        steamid = form.steam_url.data[36:]
        if steamid[-1] == '/':
            steamid = steamid[0:-1]
        steamid_response = requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='
                                        '<key>&vanityurl=' + vanityurl)
        steamid_json = steamid_response.json()
        steam_id = 0
        if steamid_json['response']['success'] == 1:
            steam_id = steamid_json['response']['steamid']
            steamid_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                            '?key=<key>&steamids=' + steam_id)
            steam_response_json = steamid_response.json()
            profile_url = steam_response_json['response']['players'][0]['avatarfull']
        if steam_id == 0:
            steamid_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                            '?key=<key>&steamids=' + steamid)
            steam_response_json = steamid_response.json()
            steam_id = steam_response_json['response']['players'][0]['steamid']
            profile_url = steam_response_json['response']['players'][0]['avatarfull']

        if form.invite_code.data == 'admin':
            user = User(name=form.name.data, nickname=form.nickname.data,
                        email=form.email.data, password=hashed_pw, steamid=steam_id, profile_url=form.steam_url.data,
                        admin=True, moderator=False, invite_code=token_hex(8), invited_by=99999,
                        profile_pic=profile_url)
        else:
            invited_by = User.query.filter_by(invite_code=form.invite_code.data).first()
            user = User(name=form.name.data, nickname=form.nickname.data,
                        email=form.email.data, password=hashed_pw, steamid=steam_id, profile_url=form.steam_url.data,
                        admin=False, moderator=False, invite_code=token_hex(8), invited_by=invited_by.id,
                        profile_pic=profile_url)
            invited_by.invites_left = invited_by.invites_left - 1
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, user=False)


@application.route('/servers', methods=['GET'])
def servers():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user.admin:
            game_servers = Servers.query.filter_by(user_id=user.id).all()
            return render_template('servers.html', email=email, servers=game_servers, title='Servers', user=user)
        return redirect(url_for('logout'))
    return redirect(url_for('login', next=request.endpoint))


@application.route('/account', methods=['GET', 'POST'])
def account():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            form = UpdateAccountForm()
            if form.validate_on_submit():
                other_user = User.query.filter_by(email=form.email.data).first()
                if other_user:
                    if other_user.id != user.id:
                        flash('Email address already taken', 'warning')
                        return redirect(url_for('account'))
                user.email = form.email.data
                user.name = form.name.data
                user.nickname = form.nickname.data
                vanityurl = form.steam_url.data[30:]
                if vanityurl[-1] == '/':
                    vanityurl = vanityurl[0:-1]
                steamid = form.steam_url.data[36:]
                if steamid[-1] == '/':
                    steamid = steamid[0:-1]
                steamid_response = requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='
                                                '<key>&vanityurl=' + vanityurl)
                steamid_json = steamid_response.json()
                steam_id = 0
                if steamid_json['response']['success'] == 1:
                    steam_id = steamid_json['response']['steamid']
                    steamid_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                                    '?key=<key>&steamids=' + steam_id)
                    steamid_response_json = steamid_response.json()
                    profile_url = steamid_response_json['response']['players'][0]['avatarfull']
                if steam_id == 0:
                    steamid_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                                                    '?key=<key>&steamids=' + steamid)
                    steam_response_json = steamid_response.json()
                    steam_id = steam_response_json['response']['players'][0]['steamid']
                    profile_url = steam_response_json['response']['players'][0]['avatarfull']
                user.steamid = steam_id
                user.profile_url = form.steam_url.data
                user.profile_pic = profile_url
                db.session.commit()
                flash("Account Information Updated Successfully!", "success")
                resp = make_response(redirect('/account'))
                resp.set_cookie('email', form.email.data)
                return resp
            elif request.method == 'GET':
                form.email.data = user.email
                form.name.data = user.name
                form.nickname.data = user.nickname
                form.steam_url.data = user.profile_url
            return render_template('account.html', email=email, form=form, user=user, title='Account')
        return redirect(url_for('logout'))
    return redirect(url_for('login', next=request.endpoint))


@application.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            form = ChangePassword()
            if form.validate_on_submit():
                if bcrypt.check_password_hash(user.password, form.password.data):
                    user.password = bcrypt.generate_password_hash(
                        form.new_password.data).decode('utf-8')
                    db.session.commit()
                    flash('Password changed successfully', 'info')
                    return redirect(url_for('account'))
                else:
                    flash('Incorrect password!, Please try again.', 'danger')
                    return redirect('changepassword')
            elif request.method == 'GET':
                form.username = user.nickname
            return render_template('change_password.html',
                                   form=form, email=email, user=user, title='Change Password')
        return redirect(url_for('logout'))
    return redirect(url_for('login', next=request.endpoint))


@application.route('/logout')
def logout():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.searching = False
            db.session.commit()
            resp = make_response(redirect(url_for('index')))
            resp.delete_cookie('email')
            return resp
        resp = make_response(redirect(url_for('index')))
        resp.delete_cookie('email')
        return resp
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('email')
    return resp


@application.route('/forgot_password')
def forgot_password():
    username = request.cookies.get('email')
    if username:
        resp = make_response(redirect('/forgot_password'))
        resp.delete_cookie('email')
        return resp
    return render_template('forgot_password.html', user=False, title='Forgot Password')


@application.route('/addserver', methods=['GET', 'POST'])
def add_server():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user.admin:
            form = AddServer()
            if form.validate_on_submit():
                server = Servers(hostname=form.hostname.data, location=form.location.data, ip=form.ip.data,
                                 password=form.password.data, user_id=user.id, port=form.port.data)
                db.session.add(server)
                db.session.commit()
                flash('Server added!', 'success')
                return redirect(url_for('servers'))
            return render_template('add_server.html', email=email, form=form, title='Add Server', user=user)
        return render_template('unauth.html', email=email, title='Unauthorised', user=user)
    return redirect(url_for('logout'))


@application.route('/play')
def play():
    email = request.cookies.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.searching = True
            db.session.commit()
            return render_template('play.html', email=email, title='Play', user=user, matchpage=True)
        return redirect(url_for('logout', next=request.endpoint))
    return redirect(url_for('logout', next=request.endpoint))
