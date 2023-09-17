import requests
from result import Result
from bs4 import BeautifulSoup

RESULTS_URL = "https://www.skysports.com/premier-league-results"


def get_results():
    results = []
    # get results by scraping the Sky sports website
    response = requests.get(RESULTS_URL)
    sky_sports_web_page = response.text

    soup = BeautifulSoup(sky_sports_web_page, "html.parser")
    wrapper_div = soup.find("div", {"class": "fixres__body callfn"})
    dates = []
    date_counter = -1
    for child in wrapper_div.find_all():
        if len(results) == 10:
            return results

        # Check to see whether element is an element of certain class which will contain date
        if "fixres__header2" in child.get("class", []):
            dates.append(child.text)
            date_counter += 1
            continue

        if len(child.contents) == 11:
            home_team = child.find_all(class_="swap-text__target")[0].text
            away_team = child.find_all(class_="swap-text__target")[1].text
            home_score = int(child.find_all(class_="matches__teamscores-side")[0].text)
            away_score = int(child.find_all(class_="matches__teamscores-side")[1].text)
            results.append(Result(home_team, away_team, dates[date_counter], home_score, away_score))


class Results:

    def __init__(self):
        self.results = get_results()

    def display_results(self):
        for result in self.results:
            print(f"{result.home_team} {result.home_score}:{result.away_score} {result.away_team}")

