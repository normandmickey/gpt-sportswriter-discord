
import requests
import json

dataSportKeys = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey=423c9b035eb2895971334e33f706c949")
dataSportKeys = dataSportKeys.json()

sport_keys = []
leagues = []

includedSports = ['American Football',
                  'Aussie Rules',
                  'Basketball',
                  'Boxing',
                  'Ice Hockey',
                  'Mixed Martial Arts',
                  'Rugby League',
                  'Soccer',
                  'Tennis']

excludedLeagues = ['icehockey_sweden_hockey_league',
                   'soccer_brazil_serie_b',
                   'soccer_korea_kleague1',
                   'soccer_mexico_ligamx',
                   'soccer_norway_eliteserien',
                   'soccer_spain_segunda_division',
                   'soccer_sweden_superettan',
                   'soccer_argentina_primera_division',
                   'soccer_brazil_campeonato',
                   'soccer_chile_campeonato',
                   'soccer_china_superleague',
                   'soccer_conmebol_copa_america',
                   'soccer_conmebol_copa_libertadores',
                   'soccer_finland_veikkausliiga',
                   'soccer_japan_j_league',
                   'soccer_league_of_ireland',
                   'soccer_sweden_allsvenskan',
                   'soccer_uefa_european_championship',
                   'soccer_belgium_first_div',
                   'soccer_denmark_superliga',
                   'soccer_efl_champ',
                   'soccer_england_efl_cup',
                   'soccer_englane_league1',
                   'soccer_england_league2',
                   'soccer_france_ligue_one',
                   'soccer_netherlands_eredivisie',
                   'soccer_turkey_super_league',
                   'soccer_uefa_champs_league_qualification',
                   'soccer_ufea_europa_conference_league',
                   'soccer_spl',
                   'baseball_milb',
                   'baseball_npb',
                   'soccer_austria_bundesliga',
                   'soccer_england_league1',
                   'soccer_germany_bundesliga',
                   'soccer_germany_bundesliga2',
                   'soccer_germany_liga3',
                   'soccer_greece_super_league',
                   'soccer_italy_serie_a',
                   'soccer_poland_ekstraklasa',
                   'soccer_portugal_primeira_liga',
                   'soccer_switzerland_superleague'
   
]
for i in range(len(dataSportKeys)):
    if (dataSportKeys[i]['has_outrights'] is False and dataSportKeys[i]['group'] in includedSports and dataSportKeys[i]['key'] not in excludedLeagues):
       sport_keys.append(dataSportKeys[i]['key'])
       leagues.append(dataSportKeys[i]['description'])

sport_keys = [i for n, i in enumerate(sport_keys) if i not in sport_keys[:n]]
leagues = [i for n, i in enumerate(leagues) if i not in leagues[:n]]


print(sport_keys)
print(leagues)