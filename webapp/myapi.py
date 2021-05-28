from flask_restful import Resource, request
from webapp import db


class MyApi(Resource):
    def get(self, serverid):
        config = {
            # 'Match': {
                'matchid': '1',
                'num_maps': '1',
                'spectators': {
                    'players': {
                        "STEAM_1:1:1021612": "admin"
                    }
                },
                'skip_veto': '1',
                'side_type': 'always_knife',
                'maplist': {
                    'de_dust2': ''
                },
                'players_per_team': '5',
                'min_players_to_ready': '1',
                'min_spectators_to_ready': '0',
                'team1': {
                    'name': 'EnVyUs NoT',
                    'flag': 'FR',
                    'logo': 'nv',
                    'players': {
                        '76561198845558570': 'freddy',
                        '76561198845558571': 'freddya',
                        '76561198845558572': 'freddyb',
                        '76561198845558573': 'freddyc',
                        '76561198845558574': 'freddyd',
                    }
                },
                'team2': {
                    'name': 'Fnatic',
                    'flag': 'SE',
                    'logo': 'fntc',
                    'players': {
                        '76561198845558575': 'freddye',
                        '76561198845558576': 'freddyf',
                        '76561198845558577': 'freddyg',
                        '76561198845558578': 'freddyh',
                        '76561198845558579': 'freddyi',
                    }
                }
            }
        # }
        return config

    def put(self, token, task):
        return {'message': 'invalid-token'}


