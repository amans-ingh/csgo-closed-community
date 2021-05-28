from webapp import sock, db
from webapp.models import User, Match, Players
import time
from flask_socketio import emit, join_room, leave_room, send

@sock.on('connect')
def connect():
    print('Client Connected')
    pass


@sock.on('disconnect')
def disconnect():
    pass


@sock.on('leave')
def client_leave(data):
    user = User.query.filter_by(socket=data['id']).first()
    if user:
        user.searching = False
        db.session.commit()


@sock.on('clientid')
def handle_client_id(data):
    room = 'match'
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        user.socket = data['id']
        db.session.commit()
        if user.searching:
            join_room(room)
        else:
            leave_room(room)
        sock.emit('clientid', 'Welcome', to=room)

    

# @sock.on('match')
# def handle_match():
#     while True:
#         users = User.query.filter_by(searching=True).all()
#         if len(users) >= 10:
#             players = users[:10]
#             match = Match()
#             db.session.add(match)
#             db.session.commit()
#             match = Match.query.filtery_by(assigned=False).first()
#             i = 0
#             for player in players:
#                 i = i + 1
#                 playerdb = Players(match_id=match.id, user_id=player.id, player_number=i)
#                 db.session.add(playerdb)
#             match.assigned = True
#             db.session.commit()
#             sock.broadcast.to()
#         time.sleep(5)
