import statsapi
import requests
import json
import datetime

def get_first_inning_stats(team_id):

    # Get last season's stats - we can get more useful data here but keeping it simple
    team_stats = statsapi.get('teams_stats',{'sportIds':1,"stats":"season", "teamId":team_id, "group":"hitting", "season":str(datetime.datetime.now().year-1)})
    print(team_stats)
    first_inning_runs = next((s['value'] for s in team_stats['stats'] if s['displayName'] == "Runs in First Inning"), 0)
    total_games = next((s['value'] for s in team_stats['stats'] if s['displayName'] == "Games Played"), 1)
    
    return int(first_inning_runs), int(total_games)

def get_team_id(team_name):
    """Retrieve team ID based on the team name."""
    teams = statsapi.get('teams', {})
    for team in teams['teams']:
        if team_name.lower() in team['name'].lower():
            return team['id']
    return None

def get_pitcher_performance(pitcher_id, opponent_id):
    """Fetch historical performance of the pitcher against the given team."""
    stats = statsapi.player_stats(pitcher_id, group="pitching", type="career")
    print(stats)
    opponent_stats = next((s for s in stats.get('stats') if s.get('group') == "pitching" and s.get('type') == "career" and s.get('teamId') == opponent_id), None)
    
    if opponent_stats:
        era = opponent_stats.get('era', 4.00)  # Default average ERA if not found
        first_inning_runs = opponent_stats.get('runsAllowedFirstInning', 0)
        total_games = opponent_stats.get('gamesPlayed', 1)
        return first_inning_runs / total_games if total_games > 0 else 0.5
    return 0.5

def get_weather_factor(location):
    """Fetch weather conditions and return a factor affecting the probability."""
    url = "https://wttr.in/" + location + "?format=%C"
    response = requests.get(url)
    if response.status_code == 200:
        conditions = response.text.lower()
        if "rain" in conditions or "storm" in conditions or "snow" in conditions:
            return 1.1  # Higher probability of NRFI due to poor conditions
        elif "windy" in conditions:
            return 1.05  # Slightly higher chance of NRFI
    return 1.0

def calculate_no_run_probability(team1, team2, pitcher1, pitcher2, location):
    """Estimate probability of no runs being scored in the first inning, incorporating additional factors."""
    team1_id = get_team_id(team1)
    team2_id = get_team_id(team2)
    
    if not team1_id or not team2_id:
        print("Invalid team name(s).")
        return
    
    t1_runs, t1_games = get_first_inning_stats(team1_id)
    t2_runs, t2_games = get_first_inning_stats(team2_id)
    
    t1_prob = 1 - (t1_runs / t1_games) if t1_games > 0 else 0.5
    t2_prob = 1 - (t2_runs / t2_games) if t2_games > 0 else 0.5
    
    p1_prob = get_pitcher_performance(pitcher1, team2_id)
    p2_prob = get_pitcher_performance(pitcher2, team1_id)
    
    weather_factor = get_weather_factor(location)
    
    no_run_prob = t1_prob * t2_prob * p1_prob * p2_prob * weather_factor
    print("Probability of a scoreless first inning between " + team1 + " and " + team2 + ": " + no_run_prob)

def get_game_id(team1, team2, game_date):
    games = statsapi.schedule(start_date=game_date, end_date=game_date)

    for game in games:
        if (team1.lower() in game['away_name'].lower() and team2.lower() in game['home_name'].lower()) or \
           (team2.lower() in game['away_name'].lower() and team1.lower() in game['home_name'].lower()):
            return game['game_id']
    
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

    game_id = input("Enter game id (leave blank to enter game details): ")
    team1 = ''
    team2 = ''
    date = ''
    
    if game_id == '' or game_id == None:
        team1 = input("Enter home team: ")
        team2 = input("Enter away team: ")
        date = input("Enter date (YYYY-MM-DD): ")
        game_id = get_game_id(team1, team2, date)
    
    gameline = statsapi.linescore(game_id)
    print(gameline)

    gameline_array = gameline.split('\n')

    team1_runs = [r for r in gameline_array[1].split(' ') if r.strip()]
    team2_runs = [r for r in gameline_array[2].split(' ') if r.strip()]

    if int(team1_runs[1]) + int(team2_runs[1]) > 0:
        print("YES RUN FIRST INNING")
    else:
        print("NO RUN FIRST INNING")
