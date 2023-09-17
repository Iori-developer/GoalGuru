from flask_login import UserMixin
from sqlalchemy.orm import relationship

from app import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

FIXTURES_API_URL = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
RAPID_API_KEY = "42dae0001amshb59fd12c2fb87f1p15e3e6jsn0946e545553a"


class Fixture(Base):
    __tablename__ = "fixtures"

    fixture_id = Column(Integer, primary_key=True)
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    game_week = Column(Integer, ForeignKey('user_game_week_score.game_week'), nullable=False)
    date = Column(String(1000))
    time = Column(String(1000))
    winner = Column(String(1000))
    active = Column(Boolean, default=False)

    def get_id(self):
        return self.fixture_id


class User(UserMixin, Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(1000), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    favourite_team = Column(String(500))

    def get_id(self):
        return self.user_id


class League(Base):
    __tablename__ = "leagues"

    league_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(1000), unique=True)

    def get_id(self):
        return self.league_id

    def set_id(self, value):
        self.league_id = value


class Prediction(Base):
    __tablename__ = "predictions"

    fixture_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)


class UserGameWeekScore(Base):
    __tablename__ = "user_game_week_score"

    user_id = Column(Integer, nullable=False, primary_key=True)
    game_week = Column(Integer, primary_key=True)
    score = Column(Integer, default=0)
