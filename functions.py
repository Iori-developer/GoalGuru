import requests
import pytz
from datetime import datetime
from models import Fixture
import config

FIXTURES_API_URL = config.API_URL


def get_fixtures(game_week_no, session):
    querystring = {"league": "39", "season": "2023", "round": f"Regular Season - {game_week_no}"}

    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(FIXTURES_API_URL, headers=headers, params=querystring)

    data = response.json()
    fixture_data = data['response']
    print(fixture_data)
    for fixture in fixture_data:
        datetime_string = fixture['fixture']['date']

        datetime_obj = datetime.fromisoformat(datetime_string)

        bst_timezone = pytz.timezone('Europe/London')
        datetime_bst = datetime_obj.astimezone(bst_timezone)

        date = datetime_bst.strftime("%d-%m-%Y")
        time = datetime_bst.strftime("%H:%M")
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']

        if fixture['teams']['home']['winner'] == 'True':
            winner = home_team
        elif fixture['teams']['away']['winner'] == 'True':
            winner = away_team
        elif fixture['score']['fulltime']['home'] == 'None':
            winner = None
        else:
            winner = 'draw'
        home_score = fixture['score']['fulltime']['home']
        away_score = fixture['score']['fulltime']['away']

        new_fixture = Fixture(
            fixture_id=fixture_id,
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            game_week=game_week_no,
            date=date,
            time=time,
            winner=winner
        )

        session.add(new_fixture)

    session.commit()
