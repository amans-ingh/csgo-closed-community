from webapp import sock, db
from webapp.models import User, Match, Matching
from flask_socketio import emit, join_room, leave_room


@sock.on('connect')
def connect():
    print('Client Connected')
    pass


@sock.on('disconnect')
def disconnect():
    pass


@sock.on('leave')
def client_leave(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        user.searching = False
        user.playing = False
        user.current_match_id = 0
        db.session.commit()


@sock.on('abandon')
def abandon(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        match = Match.query.filter_by(id=user.current_match_id).first()
        players = Matching.query.filter_by(match_id=user.current_match_id).all()
        all_players = []
        for player in players:
            user_in_mapveto = User.query.filter_by(id=player.user_id).first()
            user_in_mapveto.playing = False
            user_in_mapveto.current_match_id = 0
            user_in_mapveto.searching = False
            db.session.commit()
            all_players.append(player.user_id)
        if match.pre_match:
            emit('matchabandon', {'user_id': all_players}, broadcast = True)
        user.searching = False
        user.playing = False
        user.current_match_id = 0
        db.session.commit()


@sock.on('clientid')
def handle_client_connection(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        participants = User.query.filter_by(searching=True).all()
        if len(participants) >= 2:
            players = participants[:2]
            match = Match()
            db.session.add(match)
            db.session.commit()
            match = Match.query.filter_by(assigned=False).first()
            i = 0
            for player in players:
                i = i + 1
                playerdb = Matching(match_id=match.id, user_id=player.id, player_number=i)
                db.session.add(playerdb)
                player.searching = False
                player.playing = True
                player.current_match_id = match.id
                db.session.commit()
            match.assigned = True
            db.session.commit()
            emit('matchdetails', 'matchfound', broadcast=True)


@sock.on('match')
def handle_match(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        if user.playing:
            emit('matchdetails', 'you')


@sock.on('mapveto')
def mapveto(data):
    emit('mapveto', {'banmap': 'mirage'}, broadcast=True)
