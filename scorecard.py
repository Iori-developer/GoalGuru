from gameweek import GameWeek


class Scorecard:

    def __init__(self, game_week_no):
        self.fixtures = GameWeek(game_week_no)
        self.predictions = {}

    def get_predictions(self):
        counter = 1
        for fixture in self.fixtures.fixtures:
            print(f"What will be the score between {fixture.home_team} vs {fixture.away_team}?")
            predicted_home_score = input(f"{fixture.home_team}: ")
            predicted_away_score = input(f"{fixture.away_team}: ")
            self.predictions[counter] = {
                    "home_team": fixture.home_team,
                    "home_score": predicted_home_score,
                    "away_team": fixture.away_team,
                    "away_score": predicted_away_score
                }
            counter += 1

    def display_predictions(self):
        print("Your predictions are as follows: ")
        for i in range(1, 11):
            print(f"{self.predictions[i]['home_team']} {self.predictions[i]['home_score']} - "
                  f"{self.predictions[i]['away_score']} {self.predictions[i]['away_team']}")

