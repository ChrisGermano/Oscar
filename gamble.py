import statsapi
import requests
import json
import datetime
#from meteostat import Daily, Point
#from geopy.geocoders import Nominatim
import sys

def get_team_id(team_name):
    """Retrieve team ID based on the team name."""
    teams = statsapi.get('teams', {})
    for team in teams['teams']:
        if team_name.lower() in team['name'].lower():
            return team['id']
    return None

'''
def get_weather_factor(location):
    geolocator = Nominatim(user_agent="weather_lookup")
    location = geolocator.geocode(city)
    if not location:
        return None
    point = Point(location.latitude, location.longitude)
    start = end = datetime.strptime(date, "%Y-%m-%d")
    data = Daily(point, start, end)
    data = data.fetch()
    if data.empty:
        return None
    weather_info = {
        "temperature": data["tavg"].values[0] if "tavg" in data else None,
        "precipitation": data["prcp"].values[0] if "prcp" in data else None
    }
    return weather_info
'''

def get_game_id(team1, team2, game_date):
    try:
        games = statsapi.schedule(start_date=game_date, end_date=game_date)

        for game in games:
            if (team1.lower() in game['away_name'].lower() and team2.lower() in game['home_name'].lower()) or \
               (team2.lower() in game['away_name'].lower() and team1.lower() in game['home_name'].lower()):
                return game['game_id']
    except:
        return None


if __name__ == "__main__":
    """
    team1 = input("Enter first team name: ")
    team2 = input("Enter second team name: ")
    pitcher1 = int(input("Enter first team's starting pitcher ID: "))
    pitcher2 = int(input("Enter second team's starting pitcher ID: "))
    location = input("Enter game location: ")
    calculate_no_run_probability(team1, team2, pitcher1, pitcher2, location)
    """
    """
    p_name = input("Enter pitcher name: ")
    t_name = input("Enter team name: ")
    t_id = get_team_id(t_name)
    players = statsapi.get('sports_players', {'sportId':1,'season':2023})
    for player in players.get('people'):
        if p_name.lower() in player.get('fullName').lower():
            print(get_pitcher_performance(player['id'], t_id))
    """
    #games = statsapi.schedule(start_date='07/01/2018',end_date='07/09/2018',team=143,opponent=121)
    #gamets = statsapi.get('game_timestamps',{'gamePk':530769})
    #gamebox = statsapi.boxscore(530769,battingInfo=False,fieldingInfo=False,pitchingBox=False,gameInfo=False)

    game_id = ''
    team1 = ''
    team2 = ''
    date = ''

    if len(sys.argv) > 1:
        game_id = int(sys.argv[1])

    if game_id == '':
        game_id = input("Enter game id (leave blank to enter game details): ")
    
    if game_id == '' or game_id == None:
        team1 = input("Enter home team: ")
        team2 = input("Enter away team: ")
        date = input("Enter date (YYYY-MM-DD): ")
        game_id = get_game_id(team1, team2, date)
    

    if isinstance(game_id, int):
        gameline = statsapi.linescore(game_id)
        print(gameline)

        gameline_array = gameline.split('\n')

        team1_runs = [r for r in gameline_array[1].split(' ') if r.strip()]
        team2_runs = [r for r in gameline_array[2].split(' ') if r.strip()]

        if int(team1_runs[1]) + int(team2_runs[1]) > 0:
            print("YES RUN FIRST INNING")
        else:
            print("NO RUN FIRST INNING")
    else:
        print("INVALID GAME ID")