import unittest
from unittest.mock import patch
import requests
import pandas as pd
from io import StringIO
import script  # Remplacez par le nom du fichier contenant votre script refactorisé

class TestFootballDataScript(unittest.TestCase):

    @patch('script.requests.get')
    def test_fetch_data_for_year(self, mock_get):
        mock_response = {
            'matches': [
                {
                    'homeTeam': {'name': 'Team A'},
                    'awayTeam': {'name': 'Team B'},
                    'score': {'fullTime': {'homeTeam': 2, 'awayTeam': 1}, 'winner': 'HOME_TEAM'}
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None

        data = script.fetch_data_for_year(2020, script.headers)
        expected_data = [{
            'season': 2020,
            'team_home': 'Team A',
            'team_away': 'Team B',
            'score_home': 2,
            'score_away': 1,
            'winner': 'HOME_TEAM'
        }]
        self.assertEqual(data, expected_data)

    def test_calculate_kpis(self):
        data = [
            {'season': 2020, 'team_home': 'Team A', 'team_away': 'Team B', 'score_home': 2, 'score_away': 1, 'winner': 'HOME_TEAM'},
            {'season': 2020, 'team_home': 'Team A', 'team_away': 'Team C', 'score_home': 1, 'score_away': 1, 'winner': 'DRAW'},
            {'season': 2020, 'team_home': 'Team B', 'team_away': 'Team A', 'score_home': 0, 'score_away': 3, 'winner': 'AWAY_TEAM'}
        ]
        df = pd.DataFrame(data)
        team_stats = script.calculate_kpis(df)

        # Utilisation de StringIO pour générer la sortie attendue
        expected_output = StringIO("""season,team,games_played,goals_for,goals_against,wins,draws,losses
2020,Team A,3,6,2,2,1,0
""")
        expected_df = pd.read_csv(expected_output)
        
        pd.testing.assert_frame_equal(team_stats[team_stats['team'] == 'Team A'].reset_index(drop=True), expected_df)

if __name__ == '__main__':
    unittest.main()

