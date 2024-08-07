# To install the required packages, run:
# pip install nhlpy pandas

# Import necessary libraries
from nhlpy.nhl_client import NHLClient
import pandas as pd

# Initialize the NHL API client
client = NHLClient(verbose=True)

# Fetch all teams
teams = client.teams.teams_info()

# Prepare data for plotting
games = []
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
            try:
                games.append({
                    'home_team': game['homeTeam']['abbrev'],
                    'away_team': game['awayTeam']['abbrev'],
                    'home_score': game['homeTeam']['score'],
                    'away_score': game['awayTeam']['score']
                })
            except KeyError as e:
                print(f"Missing data in game info: {e}")
    else:
        print(f"Key 'games' not found in schedule for team {team_abbr}: {schedule}")

# Check if we have collected any games
if games:
    # Convert the data into a pandas DataFrame
    games_df = pd.DataFrame(games)

    # Export the data to a CSV file
    csv_file_path = 'nhl_2023_2024_regular_season_games.csv'
    games_df.to_csv(csv_file_path, index=False)
    print(f"Data has been exported to {csv_file_path}")
else:
    print("No games data found.")
