# To install the required packages, run:
# pip install nhlpy pandas openpyxl

# Import necessary libraries
from nhlpy.nhl_client import NHLClient
import pandas as pd

# Initialize the NHL API client
client = NHLClient(verbose=True)

# Fetch all teams
teams = client.teams.teams_info()

# Prepare data for storing games
team_games_dict = {team['abbreviation']: [] for team in teams}
searched_teams = set()  # Track searched teams to avoid duplicates

# Adjust team abbreviation from UTA to ARI if necessary
for team in teams:
    team_abbr = team['abbreviation']
    if team_abbr == 'UTA':
        team_abbr = 'ARI'
    
    if team_abbr in searched_teams:
        continue  # Skip if already searched

    try:
        schedule = client.schedule.get_season_schedule(team_abbr=team_abbr, season="20232024")
        searched_teams.add(team_abbr)  # Mark this team as searched
    except Exception as e:
        print(f"Error fetching schedule for team {team_abbr}: {e}")
        continue

    # Safely access nested structures
    if isinstance(schedule, dict) and 'games' in schedule:
        for game in schedule['games']:
            if game['gameType'] == 2:  # Filter for regular season games
                try:
                    home_team = game['homeTeam']['abbrev']
                    away_team = game['awayTeam']['abbrev']
                    game_info = {
                        'game_date': game['gameDate'],
                        'venue': game['venue']['default'],
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': game['homeTeam']['score'],
                        'away_score': game['awayTeam']['score']
                    }
                    # Add game to home and away teams' lists
                    if home_team in team_games_dict:
                        team_games_dict[home_team].append(game_info)
                    if away_team in team_games_dict:
                        team_games_dict[away_team].append(game_info)
                except KeyError as e:
                    print(f"Missing data in game info: {e}")
    else:
        print(f"Key 'games' not found in schedule for team {team_abbr}: {schedule}")

# Remove duplicate games and ensure each team has 82 games
for team_abbr, games_list in team_games_dict.items():
    # Convert list of games to DataFrame
    df = pd.DataFrame(games_list)
    # Remove duplicates
    df = df.drop_duplicates(subset=['game_date', 'home_team', 'away_team'])
    # Check the number of games
    if len(df) != 82:
        print(f"Warning: {team_abbr} does not have exactly 82 games. Found {len(df)} games.")
    # Update the dictionary with the cleaned DataFrame
    team_games_dict[team_abbr] = df

# Export the data to an Excel file with separate sheets for each team
excel_file_path = 'nhl_2023_2024_regular_season_games.xlsx'
with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
    for team_abbr, df in team_games_dict.items():
        df.to_excel(writer, sheet_name=team_abbr, index=False)

print(f"Data has been exported to {excel_file_path}")
