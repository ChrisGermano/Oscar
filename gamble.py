import statsapi
import requests

def get_first_inning_stats(team_id):
    """Fetch first-inning run statistics for a given team."""
    team_stats = statsapi.team_stats(teamId=team_id, group="hitting", type="season")
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
    opponent_stats = next((s for s in stats['stats'] if s['group'] == "pitching" and s['type'] == "career" and s['teamId'] == opponent_id), None)
    
    if opponent_stats:
        era = opponent_stats.get('era', 4.00)  # Default average ERA if not found
        first_inning_runs = opponent_stats.get('runsAllowedFirstInning', 0)
        total_games = opponent_stats.get('gamesPlayed', 1)
        return first_inning_runs / total_games if total_games > 0 else 0.5
    return 0.5

def get_weather_factor(location):
    """Fetch weather conditions and return a factor affecting the probability."""
    url = f"https://wttr.in/{location}?format=%C"
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
    print(f"Probability of a scoreless first inning between {team1} and {team2}: {no_run_prob:.2%}")

if __name__ == "__main__":
    team1 = input("Enter first team name: ")
    team2 = input("Enter second team name: ")
    pitcher1 = int(input("Enter first team's starting pitcher ID: "))
    pitcher2 = int(input("Enter second team's starting pitcher ID: "))
    location = input("Enter game location: ")
    calculate_no_run_probability(team1, team2, pitcher1, pitcher2, location)
