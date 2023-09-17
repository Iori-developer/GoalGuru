from fixture import Fixture


class Result(Fixture):

    def __init__(self, home_team, home_team_badge, away_team, away_team_badge, date, time, home_score, away_score):
        super().__init__(home_team, home_team_badge, away_team, away_team_badge, date, time)
        self.home_score = home_score
        self.away_score = away_score
