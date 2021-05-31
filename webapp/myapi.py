from flask_restful import Resource
from webapp.models import Match, User, Matching
from webapp.functions import MyClass


class GenerateConfig:
    def __init__(self, match_id):
        self.match_id = match_id

    def find_maps(self):
        match = Match.query.filter_by(id=self.match_id).first()
        map_finder = MyClass()
        maps_to_play = {}
        maps_to_be_played = map_finder.maps_names(match.maps)
        for maps in maps_to_be_played:
            maps_to_play[maps] = ''
        return maps_to_play

    def find_teams(self):
        team_a = {}
        team_b = {}
        matchings = Matching.query.filter_by(match_id=self.match_id).all()
        for matching in matchings:
            if matching.player_number == 1:
                user = User.query.filter_by(id=matching.user_id).first()
                team_name = 'team_' + user.nickname
                team_a['name'] = team_name
                team_a['flag'] = 'FR'
                team_a['logo'] = 'nipta'
                team_a['players'] = {}
            if matching.player_number == 2:
                user = User.query.filter_by(id=matching.user_id).first()
                team_name = 'team_' + user.nickname
                team_b['name'] = team_name
                team_b['flag'] = 'SE'
                team_b['logo'] = 'niptb'
                team_b['players'] = {}
            if matching.player_number % 2:
                user = User.query.filter_by(id=matching.user_id).first()
                team_a['players'][user.steamid] = user.nickname
            else:
                user = User.query.filter_by(id=matching.user_id).first()
                team_b['players'][user.steamid] = user.nickname
        return team_a, team_b


class MyApi(Resource):
    def get(self, match_id):
        config_generator = GenerateConfig(match_id)
        (team_a, team_b) = config_generator.find_teams()
        config = {'matchid': match_id,
                  'num_maps': '1',
                  'skip_veto': '1',
                  'side_type': 'always_knife',
                  'maplist': config_generator.find_maps(),
                  'players_per_team': '5',
                  'min_players_to_ready': '1',
                  'min_spectators_to_ready': '0',
                  'team1': team_a,
                  'team2': team_b
        }
        return config

    def put(self, token):
        return {'message': 'invalid-token'}
