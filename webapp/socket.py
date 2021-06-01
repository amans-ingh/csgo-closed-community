from webapp import sock, db
from webapp.models import User, Match, Matching, Servers, Team
from flask_socketio import emit
from webapp.functions import MyClass
from webapp.rcon import GameServer
from webapp import application
import random


@sock.on('connect')
def connect():
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
        if match:
            if match.status == 1:
                players = Matching.query.filter_by(match_id=user.current_match_id).all()
                all_players = []
                for player in players:
                    user_in_mapveto = User.query.filter_by(id=player.user_id).first()
                    user_in_mapveto.playing = False
                    user_in_mapveto.current_match_id = 0
                    user_in_mapveto.searching = False
                    db.session.commit()
                    all_players.append(player.user_id)
                    match.status = 4
                    emit('matchabandon', {'user_id': all_players}, broadcast=True)
            user.searching = False
            user.playing = False
            user.current_match_id = 0
            db.session.commit()


@sock.on('clientid')
def handle_client_connection(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        if user.searching:
            participants = User.query.filter_by(searching=True).all()
            server = Servers.query.filter_by(busy=False).first()
            if len(participants) >= 2 and server:
                server.busy = True
                random.shuffle(participants)
                players = participants[:2]
                match = Match()
                db.session.add(match)
                db.session.commit()
                match = Match.query.filter_by(status=0).first()
                i = 0
                team_a = Team(name='team_' + players[0].nickname, captain=players[0].id,
                              p1=players[0].id,
                              # p2=players[2].id,
                              # p3=players[4].id,
                              # p4=players[6].id,
                              # p5=players[8].id,
                              current_match_id=match.id
                              )
                team_b = Team(name='team_' + players[1].nickname, captain=players[1].id,
                              p1=players[1].id,
                              # p2=players[3].id,
                              # p3=players[5].id,
                              # p4=players[7].id,
                              # p5=players[9].id,
                              current_match_id=match.id
                              )
                match.server_id = server.id
                db.session.add(team_a)
                db.session.add(team_b)
                db.session.commit()
                for player in players:
                    i = i + 1
                    matching = Matching(match_id=match.id, user_id=player.id, player_number=i)
                    db.session.add(matching)
                    player.searching = False
                    player.playing = True
                    player.current_match_id = match.id
                    db.session.commit()
                teams = Team.query.filter_by(current_match_id=match.id).all()
                match.team1_id = teams[0].id
                match.team2_id = teams[1].id
                match.status = 1
                db.session.commit()
                emit('matchdetails', 'matchfound', broadcast=True)
        if user.playing:
            match = Match.query.filter_by(id=user.current_match_id).first()
            if match.status == 1:
                my_class = MyClass()
                map_list = my_class.maps_names(match.maps)
                banned_maps = ['mirage', 'inferno', 'overpass', 'nuke', 'train', 'dust2', 'vertigo']
                for veto_map in map_list:
                    banned_maps.remove(veto_map)
                emit('matchpage', {'mapsbanned': banned_maps, 'finalmap': False, 'ip': False})
                team_a = Team.query.filter_by(id=match.team1_id).first()
                team_b = Team.query.filter_by(id=match.team2_id).first()
                emit('mapvetocaptain', {'capt1': team_a.captain,
                                        'capt2': team_b.captain,
                                        'maps_avail': map_list,
                                        'turn': match.turn}, broadcast=True)
            elif match.status == 2:
                my_class = MyClass()
                map_list = my_class.maps_names(match.maps)
                emit('matchpage', {'mapsbanned': False, 'finalmap': map_list[0], 'ip': match.ip})


@sock.on('match')
def handle_match(data):
    user = User.query.filter_by(id=data['user_id']).first()
    if user:
        if user.playing:
            emit('matchdetails', 'you')


@sock.on('mapveto')
def mapveto(data):
    user = User.query.filter_by(id=data['userid']).first()
    match = Match.query.filter_by(id=user.current_match_id).first()
    if match:
        team_a = Team.query.filter_by(id=match.team1_id).first()
        team_b = Team.query.filter_by(id=match.team2_id).first()
        if team_a.captain == data['userid'] or team_b.captain == data['userid']:
            other_users = User.query.filter_by(current_match_id=user.current_match_id).all()
            all_players = []
            for users in other_users:
                all_players.append(users.id)
            maps_available = MyClass().maps(match.maps)
            num_maps_avail = MyClass().maps_left(maps_available)
            maps_names = MyClass().maps_names(match.maps)
            map_weight = MyClass().weight_of_map(data['banmap'])
            if num_maps_avail > 1:
                if data['banmap'] in maps_names:
                    match.maps = match.maps - map_weight
                    maps_names = MyClass().maps_names(match.maps)
                    num_maps_avail = num_maps_avail - 1
                    emit('mapvetoclient', {'user_id': all_players,
                                           'banmap': data['banmap'],
                                           'ip': False,
                                           'map': False,
                                           'turn': not match.turn}, broadcast=True)
                    emit('mapvetocaptain', {'capt1': team_a.captain,
                                            'capt2': team_b.captain,
                                            'maps_avail': maps_names,
                                            'turn': not match.turn}, broadcast=True)
                    if match.turn:
                        match.turn = False
                    else:
                        match.turn = True
                db.session.commit()
            if num_maps_avail == 1:
                match = Match.query.filter_by(id=user.current_match_id).first()
                server = Servers.query.get(match.server_id)
                if server:
                    match.server_id = server.id
                    match.api = application.config['SERVER_URL']
                    server.busy = True
                    match_ip = 'steam://connect/' + server.ip + ':' + str(server.port)
                    match.ip = match_ip
                    match.status = 2
                    map_chosen = MyClass().maps_names(match.maps)
                    db.session.commit()
                    server_config = GameServer(server.ip, server.port, server.password, match.id)
                    server_config.load_match()
                    emit('mapvetoclient', {'user_id': all_players,
                                           'map': map_chosen[0],
                                           'ip': 'steam://connect/' + server.ip + ':' + str(server.port),
                                           'banmap': False,
                                           'turn': False}, broadcast=True)
