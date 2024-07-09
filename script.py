import requests
import pandas as pd

# identification de l'API 
API_TOKEN = '12abfbaacdab48bc8948ed6061925e1f'

headers = {
    'X-Auth-Token': API_TOKEN
}

def fetch_data_for_year(year, headers):
    url = f'https://api.football-data.org/v2/competitions/PL/matches?season={year}'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        return [
            {
                'season': year,
                'team_home': match['homeTeam']['name'],
                'team_away': match['awayTeam']['name'],
                'score_home': match['score']['fullTime']['homeTeam'],
                'score_away': match['score']['fullTime']['awayTeam'],
                'winner': match['score']['winner']
            }
            for match in matches
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for year {year}: {e}")
        return []

def fetch_all_data(years, headers):
    data = []
    for year in years:
        data.extend(fetch_data_for_year(year, headers))
    return data

def calculate_kpis(df):
    home_stats = df.groupby(['season', 'team_home']).agg(
        games_played_home=('team_home', 'count'),
        goals_for_home=('score_home', 'sum'),
        goals_against_home=('score_away', 'sum'),
        wins_home=('winner', lambda x: (x == 'HOME_TEAM').sum()),
        draws_home=('winner', lambda x: (x == 'DRAW').sum()),
        losses_home=('winner', lambda x: (x == 'AWAY_TEAM').sum())
    ).reset_index()

    away_stats = df.groupby(['season', 'team_away']).agg(
        games_played_away=('team_away', 'count'),
        goals_for_away=('score_away', 'sum'),
        goals_against_away=('score_home', 'sum'),
        wins_away=('winner', lambda x: (x == 'AWAY_TEAM').sum()),
        draws_away=('winner', lambda x: (x == 'DRAW').sum()),
        losses_away=('winner', lambda x: (x == 'HOME_TEAM').sum())
    ).reset_index()

    team_stats = pd.merge(home_stats, away_stats, left_on=['season', 'team_home'], right_on=['season', 'team_away'])

    team_stats['games_played'] = team_stats['games_played_home'] + team_stats['games_played_away']
    team_stats['goals_for'] = team_stats['goals_for_home'] + team_stats['goals_for_away']
    team_stats['goals_against'] = team_stats['goals_against_home'] + team_stats['goals_against_away']
    team_stats['wins'] = team_stats['wins_home'] + team_stats['wins_away']
    team_stats['draws'] = team_stats['draws_home'] + team_stats['draws_away']
    team_stats['losses'] = team_stats['losses_home'] + team_stats['losses_away']

    team_stats = team_stats[['season', 'team_home', 'games_played', 'goals_for', 'goals_against', 'wins', 'draws', 'losses']]
    team_stats.columns = ['season', 'team', 'games_played', 'goals_for', 'goals_against', 'wins', 'draws', 'losses']

    return team_stats

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    years = [2020, 2021, 2022, 2023]
    data = fetch_all_data(years, headers)
    df = pd.DataFrame(data)
    team_stats = calculate_kpis(df)
    save_to_csv(team_stats, 'Teams_stats.csv')

