import pytz
import requests
from models import Fixture
from bs4 import BeautifulSoup
from datetime import datetime

FIXTURES_URL = "https://www.skysports.com/premier-league-fixtures"
FIXTURES_API_URL = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
RAPID_API_KEY = "42dae0001amshb59fd12c2fb87f1p15e3e6jsn0946e545553a"


# def get_fixtures():
#     fixtures = []
#     # get fixtures by scraping the Sky sports website
#     response = requests.get(FIXTURES_URL)
#     google_prem_web_page = response.text
#
#     soup = BeautifulSoup(google_prem_web_page, "html.parser")
#     wrapper_div = soup.find("div", {"class": "fixres__body callfn"})
#     dates = []
#     date_counter = -1
#     for child in wrapper_div.find_all():
#         # Check to see if element is one showing fixture but with no betting odds
#         # (This means that it is not part of the upcoming fixture list)
#         if child.get('class')[0] == "fixres__item" and len(child.contents) == 3:
#             return fixtures
#
#         # Check to see whether element is an element of certain class which will contain date
#         if "fixres__header2" in child.get("class", []):
#             dates.append(child.text)
#             date_counter += 1
#             continue
#
#         # Check to see whether element is an element of certain class which will have our fixture in it
#         if child.get('class')[0] == "fixres__item" and len(child.contents) == 5:
#             home_team = child.find_all(class_="swap-text__target")[0].text
#             away_team = child.find_all(class_="swap-text__target")[1].text
#             fixtures.append(Fixture(home_team, away_team, dates[date_counter]))


class GameWeek:

    def __init__(self, game_week_no):
        self.game_week_no = game_week_no
        self.fixtures = self.get_fixtures_api()
        # Will eventually equal a Results object depending on the date
        self.results = []

    def display_fixtures(self):
        for fixture in self.fixtures:
            print(f"{fixture.home_team} Vs {fixture.away_team} on {fixture.date} at {fixture.time}")

    def get_fixtures_api(self):
        querystring = {"league": "39", "season": "2023", "round": f"Regular Season - {self.game_week_no}"}

        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.get(FIXTURES_API_URL, headers=headers, params=querystring)

        fixtures = []
        data = response.json()
        fixture_data = data['response']
        for fixture in fixture_data:
            datetime_string = fixture['fixture']['date']

            datetime_obj = datetime.fromisoformat(datetime_string)

            bst_timezone = pytz.timezone('Europe/London')
            datetime_bst = datetime_obj.astimezone(bst_timezone)

            date = datetime_bst.strftime("%d-%m-%Y")
            time = datetime_bst.strftime("%H:%M")

            home_team = fixture['teams']['home']['name']
            home_team_badge = fixture['teams']['home']['logo']
            away_team = fixture['teams']['away']['name']
            away_team_badge = fixture['teams']['away']['logo']
            new_fixture = Fixture(home_team, home_team_badge, away_team, away_team_badge, date, time)
            fixtures.append(new_fixture)

        return fixtures


# game_week = GameWeek(3)
# game_week.display_fixtures()
