import requests
from webapp import application


class SteamAPI:
    def steam_id_profile(self, url):
        try:
            vanity_url = url[30:]
            if vanity_url[-1] == '/':
                vanity_url = vanity_url[0:-1]
            steam_id = url[36:]
            if steam_id[-1] == '/':
                steam_id = steam_id[0:-1]
        except:
            vanity_url = url
            steam_id = url
        steam_response = requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' +
                                      application.config['STEAM_API_KEY'] + '&vanityurl=' + vanity_url)
        steam_json = steam_response.json()
        if steam_json['response']['success'] == 1:
            steam_id_final = steam_json['response']['steamid']
            steam_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' +
                                          application.config['STEAM_API_KEY'] + '&steamids=' + steam_id_final)
            steam_json = steam_response.json()
            profile_pic = steam_json['response']['players'][0]['avatarfull']
            profile_url = steam_json['response']['players'][0]['profileurl']
        else:
            steam_response = requests.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' +
                                          application.config['STEAM_API_KEY'] + '&steamids=' + steam_id)
            steam_json = steam_response.json()
            if steam_json['response']['players']:
                steam_id_final = steam_json['response']['players'][0]['steamid']
                profile_pic = steam_json['response']['players'][0]['avatarfull']
                profile_url = steam_json['response']['players'][0]['profileurl']
            else:
                steam_id_final = False
                profile_pic = False
                profile_url = False

        return steam_id_final, profile_pic, profile_url

    def game_hours(self, steam_id):
        response = requests.get('http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key='
                                + application.config['STEAM_API_KEY'] + '&steamid=' + steam_id)
        response_json = response.json()
        steam_hours = response_json['playerstats']['stats'][2]['value']
        return steam_hours