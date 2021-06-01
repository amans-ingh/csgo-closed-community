from webapp import db, login_manager
from flask_login import UserMixin
from flask import redirect, url_for, request


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.endpoint))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    steamid = db.Column(db.String(20), nullable=False)
    profile_url = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    searching = db.Column(db.Boolean, nullable=False, default=False)
    moderator = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    invite_code = db.Column(db.String, nullable=False, unique=True)
    invites_left = db.Column(db.Integer, nullable=False, default=3)
    current_match_id = db.Column(db.Integer, nullable=True)
    invited_by = db.Column(db.Integer)
    profile_pic = db.Column(db.String, nullable=False)
    playing = db.Column(db.Boolean, nullable=False, default=False)
    matches = db.relationship('Matching', backref='player', lazy=True)



class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api = db.Column(db.String)
    status = db.Column(db.Integer, nullable=False, default=0)
    maps = db.Column(db.Integer, nullable=False, default=127)
    ip = db.Column(db.String)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    turn = db.Column(db.Boolean, default=True)
    winner = db.Column(db.Integer, db.ForeignKey('team.id'))
    matches = db.relationship('Matching', backref='match', lazy=True)
    abandoned = db.Column(db.Boolean, default=False)
    forfeit = db.Column(db.Boolean, default=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    team1_score = db.Column(db.Integer)
    team2_score = db.Column(db.Integer)


class Matching(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_number = db.Column(db.Integer, nullable=False)


class Servers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    busy = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.String, nullable=False)
    ongoing_match = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_match_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(15), nullable=False)
    flag = db.Column(db.String(2), nullable=False, default='FR')
    logo = db.Column(db.String(4), nullable=False, default='nip')
    captain = db.Column(db.Integer, nullable=False)
    permanent_team = db.Column(db.Boolean, nullable=False, default=False)
    p1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    p2 = db.Column(db.Integer, db.ForeignKey('user.id'))
    p3 = db.Column(db.Integer, db.ForeignKey('user.id'))
    p4 = db.Column(db.Integer, db.ForeignKey('user.id'))
    p5 = db.Column(db.Integer, db.ForeignKey('user.id'))


class MapStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    map_number = db.Column(db.Integer)
    map_name = db.Column(db.String(64))
    winner = db.Column(db.Integer, db.ForeignKey('team.id'))
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    player_stats = db.relationship('PlayerStats', backref='mapstats', lazy='dynamic')


class PlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    map_id = db.Column(db.Integer, db.ForeignKey('map_stats.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    steam_id = db.Column(db.String(40))
    name = db.Column(db.String(40))
    kills = db.Column(db.Integer, default=0)
    deaths = db.Column(db.Integer, default=0)
    roundsplayed = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    flashbang_assists = db.Column(db.Integer, default=0)
    teamkills = db.Column(db.Integer, default=0)
    suicides = db.Column(db.Integer, default=0)
    headshot_kills = db.Column(db.Integer, default=0)
    damage = db.Column(db.Integer, default=0)
    bomb_plants = db.Column(db.Integer, default=0)
    bomb_defuses = db.Column(db.Integer, default=0)
    v1 = db.Column(db.Integer, default=0)
    v2 = db.Column(db.Integer, default=0)
    v3 = db.Column(db.Integer, default=0)
    v4 = db.Column(db.Integer, default=0)
    v5 = db.Column(db.Integer, default=0)
    k1 = db.Column(db.Integer, default=0)
    k2 = db.Column(db.Integer, default=0)
    k3 = db.Column(db.Integer, default=0)
    k4 = db.Column(db.Integer, default=0)
    k5 = db.Column(db.Integer, default=0)
    firstkill_t = db.Column(db.Integer, default=0)
    firstkill_ct = db.Column(db.Integer, default=0)
    firstdeath_t = db.Column(db.Integer, default=0)
    firstdeath_Ct = db.Column(db.Integer, default=0)
