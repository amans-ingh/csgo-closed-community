from webapp import db


class User(db.Model):
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
    socket = db.Column(db.String, nullable=True)
    invited_by = db.Column(db.Integer)
    profile_pic = db.Column(db.String, nullable=False)
    playing = db.Column(db.Boolean, nullable=False, default=False)
    matches = db.relationship('Players', backref='player', lazy=True)
    server = db.relationship('Servers', backref='owner', lazy=True)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assigned = db.Column(db.Boolean, nullable=False, default=False)
    matches = db.relationship('Players', backref='match', lazy=True)


class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_number = db.Column(db.Integer, nullable=False)


class Servers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String, nullable=False, unique=True)
    location = db.Column(db.String, nullable=False)
    busy = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.String, nullable=False)
    ongoing_match = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
