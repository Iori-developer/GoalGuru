from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, jsonify
# from sqlite3 import IntegrityError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, Base
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy import Column, Integer, ForeignKey, create_engine, Table, func, select
from sqlalchemy.orm import relationship, Session
from models import *
from config import engine_url

current_game_week = 3

teams = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion", "Burnley", "Chelsea",
         "Crystal Palace", "Everton", "Fulham", "Liverpool", "Luton Town", "Manchester City", "Manchester United",
         "Newcastle United", "Nottingham Forest", "Sheffield United", "Tottenham Hotspur", "West Ham United",
         "Wolverhampton Wanderers"]

# Create an association table for the many-to-many relationship
league_user_association = Table('league_user_association', Base.metadata,
                                Column('league_id', Integer, ForeignKey('leagues')),
                                Column('user_id', Integer, ForeignKey('users'))
                                )

# Define the relationships
User.leagues = relationship("League", secondary=league_user_association, back_populates="users")
League.users = relationship("User", secondary=league_user_association, back_populates="leagues")

# Create and use the database
engine = create_engine(engine_url)
Base.metadata.create_all(engine)

session = Session(engine)

# Configure Flask-Login's login manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    user = session.query(User).get(int(user_id))
    return user


# with app.app_context():
#     # db.drop_all()
#     Base.create_all()


def check_current_game_week():
    global current_game_week
    current_date = datetime.now()
    update_current_game_week = False

    fixtures = session.query(Fixture).filter_by(game_week=current_game_week)

    for fixture in fixtures:
        test_date = datetime.strptime(fixture.date, "%d-%m-%Y")
        if test_date <= current_date:
            update_current_game_week = True
            break

    if update_current_game_week:
        current_game_week += 1
        for fixture in fixtures:
            fixture.active = update_current_game_week

    print(current_game_week)


def update_weekly_scores():
    user_ids = [user[0] for user in session.execute(select(User.user_id))]
    for user in user_ids:
        print(user)
        # Get the fixtures relevant to the current game week
        fixtures = session.query(Fixture).filter_by(game_week=current_game_week)

        # Get the results of these fixtures
        results = {}
        for fixture in fixtures:
            results[fixture.fixture_id] = {
                'home_score': fixture.home_score,
                'away_score': fixture.away_score
            }

        try:
            # Get the user's predictions of the current week's fixtures
            user_predictions = {}
            for result in results:
                prediction = session.query(Prediction).filter_by(fixture_id=result, user_id=user).first()

                user_predictions[prediction.fixture_id] = {
                    "home_score": prediction.home_score,
                    "away_score": prediction.away_score
                }

            # Compare and give points based on predictions and results
            weekly_score = 0
            for fixture_id, scores in user_predictions.items():
                prediction_home = int(scores['home_score'])
                prediction_away = int(scores['away_score'])

                try:
                    result_home = int(results[fixture_id]['home_score'])
                    result_away = int(results[fixture_id]['away_score'])
                except TypeError as e:
                    print(e)
                    print("Match has been postponed or cancelled")
                else:
                    # Correct result and score
                    if prediction_home == result_home and prediction_away == result_away:
                        weekly_score += 10
                        continue

                    # You only got the number of goals right but not the result
                    if prediction_home + prediction_away == result_home + result_away:
                        weekly_score += 1
                        continue

                    # Home team to win
                    if prediction_home > prediction_away and result_home > result_away:
                        weekly_score += 4
                        # Correct goal difference
                        if prediction_home - prediction_away == result_home - result_away:
                            weekly_score += 2
                    # Away team to win
                    elif prediction_away > prediction_home and result_away > result_home:
                        weekly_score += 4
                        # Correct goal difference
                        if prediction_away - prediction_home == result_away - result_home:
                            weekly_score += 2
                    # Draw
                    elif prediction_home == prediction_away and result_home == result_away:
                        weekly_score += 5

            print("JUST ABOUT TO SUBMIT SCORES TO DB")
            try:
                new_data_entry = UserGameWeekScore(
                    user_id=user,
                    game_week=current_game_week,
                    score=weekly_score
                )

                session.add(new_data_entry)
                session.commit()
            except IntegrityError as e:
                print(e)
                session.rollback()
        except AttributeError as e:
            print(e)


def get_score(user_id):
    scores = session.query(UserGameWeekScore).filter_by(user_id=user_id).all()
    overall_score = 0
    for score in scores:
        overall_score += score.score

    return overall_score


# update_weekly_scores()


# check_current_game_week()


@app.route("/")
def index():
    if current_user.is_authenticated:
        logout_user()
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        result = session.query(User).filter(User.email == email)
        # result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Check stored password hash against entered password hashed.
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        result = session.query(User).filter(User.email == email)
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return render_template("register.html", teams=teams)

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=request.form.get('email'),
            username=request.form.get('username'),
            password=hash_and_salted_password,
            favourite_team=request.form.get('team')
        )

        session.add(new_user)
        session.commit()

        # Log in and authenticate user after adding to database
        login_user(new_user)

        return redirect(url_for('home'))

    return render_template("register.html", teams=teams, logged_in=current_user.is_authenticated)


@app.route("/home")
@login_required
def home():
    current_url = request.url

    leagues_data = []
    for league in current_user.leagues:
        members_count = session.query(func.count(league_user_association.c.user_id)).filter(
            league_user_association.c.league_id == league.league_id
        ).scalar()

        # Query for user_ids in the specified league
        user_ids = session.query(User.user_id).join(League.users).filter(League.league_id == league.league_id).all()

        # Extract the user IDs from the result
        user_ids = [user_id for (user_id,) in user_ids]

        player_scores = []
        for user in user_ids:
            score = get_score(user)
            data = {
                'user_id': user,
                'score': score
            }
            player_scores.append(data)
            player_scores = sorted(player_scores, key=lambda x: x["score"], reverse=True)

        rank = None
        for i, item in enumerate(player_scores):
            if item['user_id'] == current_user.get_id():
                rank = i + 1
                break

        if members_count is not None:
            response_data = {
                'league_name': league.name,
                'members_count': members_count,
                'rank': rank
            }
            leagues_data.append(response_data)
        else:
            print("League has no members or no league found")

    overall_score = get_score(current_user.get_id())

    return render_template("home.html", logged_in=True, current_url=current_url, leagues=leagues_data,
                           overall_score=overall_score)


@app.route("/predictions", methods=['POST', 'GET'])
@login_required
def predictions():
    return render_template("predictions.html", logged_in=True)


@app.route("/create_league", methods=['POST', 'GET'])
@login_required
def create_league():
    try:
        new_league = League(
            name=request.form.get('league-name')
        )

        session.add(new_league)
        session.commit()

        response = {"message": "Data successfully processed"}
        return jsonify(response)
    except IntegrityError as e:
        session.rollback()
        response = {'message': "Sorry, this league name already exists"}
        return jsonify(response)
    except Exception as e:
        print(e)
        response = {'message': "Sorry, issue with processing data. Please try again"}
        return jsonify(response)


@app.route("/join_league", methods=['POST', 'GET'])
@login_required
def join_league():
    try:
        # Check to see if league exists and then add a user
        if request.method == "POST":
            league_name = request.form.get('league-name')
            result = session.query(League).filter(League.name == league_name)
            league = result.scalar()
            if league:
                query = session.query(league_user_association).join(League).join(User).filter(
                    League.name == league_name,
                    User.user_id == current_user.get_id()
                )
                entry_exists = session.query(query.exists()).scalar()
                if not entry_exists:
                    # This creates the entry in the association table
                    league.users.append(current_user)
                    session.commit()

                    response = {"message": "Successfully joined league"}
                    return jsonify(response)
                else:
                    response = {"message": "Already a member of the league"}
                    return jsonify(response)
            else:
                response = {"message": "Try again, league does not exist"}
                return jsonify(response)
    except Exception as e:
        print(e)
        response = {'message': "Sorry, issue with processing data. Please try again"}
        return jsonify(response)


@app.route("/filter_game_week", methods=['POST', 'GET'])
@login_required
def filter_game_week():
    if request.method == 'POST':
        game_week_no = int(request.form.get('game-week'))
        user_id = request.form.get('user')
        username = session.query(User).filter_by(user_id=user_id).first().username

        fixtures_in_game_week = session.query(Fixture).filter_by(game_week=game_week_no).all()
        fixtures_information = [{
            'fixture_id': fixture.fixture_id,
            'home_team': fixture.home_team,
            'home_score': fixture.home_score,
            'away_team': fixture.away_team,
            'away_score': fixture.away_score
        } for fixture in fixtures_in_game_week]

        formatted_fixtures = [{'home_team': fixture.home_team, 'away_team': fixture.away_team} for fixture in
                              fixtures_in_game_week]

        formatted_fixtures.append({'username': username})

        # predictions will be active
        if game_week_no == current_game_week:

            formatted_fixtures.append({'message': 'active'})

            return jsonify(formatted_fixtures)
        elif game_week_no > current_game_week:

            formatted_fixtures.append({'message': 'future'})

            return jsonify(formatted_fixtures)
        else:
            # Get the results of the previous matches
            previous_results = []
            for fixture in fixtures_information:
                try:
                    result = {'home_score': fixture['home_score'],
                              'away_score': fixture['away_score']}
                except AttributeError as e:
                    print(e)
                    result = {'home_score': 'Match Postponed',
                              'away_score': 'Match Postponed'}

                    previous_results.append(result)
                else:
                    previous_results.append(result)

            # Get the previous predictions from db
            try:
                previous_predictions = []
                for fixture in fixtures_information:
                    prediction = session.query(Prediction).filter_by(fixture_id=fixture['fixture_id'],
                                                                     user_id=user_id).first()
                    data = {
                        'home_team': fixture['home_team'],
                        'home_score': prediction.home_score,
                        'away_team': fixture['away_team'],
                        'away_score': prediction.away_score
                    }
                    previous_predictions.append(data)

                previous_predictions.append({
                    'username': username
                })

                weekly_score = session.query(UserGameWeekScore).filter_by(user_id=user_id,
                                                                          game_week=game_week_no).first()
                previous_predictions.append({
                    'score': weekly_score.score
                })

                previous_predictions.append(previous_results)
                previous_predictions.append({'message': 'past-predictions'})

                return jsonify(previous_predictions)
            except TypeError as e:
                print(e)
                print("No prediction made")
                formatted_fixtures.append(previous_results)
                formatted_fixtures.append({'message': 'past-no-predictions'})

                return jsonify(formatted_fixtures)
            except AttributeError as e:
                print(e)
                print("No prediction made")
                formatted_fixtures.append(previous_results)
                formatted_fixtures.append({'message': 'past-no-predictions'})

                return jsonify(formatted_fixtures)


@app.route("/process_predictions", methods=['POST', 'GET'])
@login_required
def process_predictions():
    if request.method == 'POST':
        data = request.form
        items = list(data.items())

        home_score = 0
        away_score = 0
        home_team = ""
        away_team = ""
        for i in range(20):
            if i % 2 == 0:
                if items[i][1] == "":
                    home_score = 0
                else:
                    home_score = items[i][1]

                home_team = items[i][0]
            else:
                if items[i][1] == "":
                    away_score = 0
                else:
                    away_score = items[i][1]

                away_team = items[i][0]

                fixture_id = session.query(Fixture).filter_by(home_team=home_team, away_team=away_team,
                                                              game_week=current_game_week).first()
                if fixture_id:
                    fixture_id = fixture_id.fixture_id
                else:
                    fixture_id = False

                try:
                    new_prediction = Prediction(
                        fixture_id=fixture_id,
                        user_id=current_user.get_id(),
                        home_score=home_score,
                        away_score=away_score
                    )

                    session.add(new_prediction)
                    session.commit()

                except IntegrityError as e:
                    session.rollback()
                    print(e)

                    prediction = session.query(Prediction).filter_by(fixture_id=fixture_id,
                                                                     user_id=current_user.get_id()).first()
                    prediction.home_score = home_score
                    prediction.away_score = away_score

                    session.commit()

        return redirect(url_for("predictions"))


@app.route("/league", methods=['POST', 'GET'])
@login_required
def league():
    league_name = request.args.get('league')
    league_data = session.query(League).filter_by(name=league_name).first()
    user_ids = [value[1] for value in session.query(league_user_association).filter_by(league_id=league_data.league_id).all()]
    user_data = [session.query(User).filter_by(user_id=user_id).first() for user_id in user_ids]
    for i in range(len(user_data)):
        score = get_score(user_data[i].user_id)
        user_data[i] = {
            'user_model': user_data[i],
            'score': score
        }
    sorted_user_data = sorted(user_data, key=lambda x: x['score'], reverse=True)
    return render_template("league.html", logged_in=True, league_name=league_name, user_data=sorted_user_data)


@app.route("/rival_predictions", methods=["POST", "GET"])
@login_required
def rival_predictions():
    username = request.args.get('username')
    user_id = request.args.get('user_id')
    return render_template('rival-predictions.html', logged_in=True, current_game_week=current_game_week, username=username, user_id=user_id)


if __name__ == "__main__":
    app.run(debug=True)

# Example of creating a Fixture and associating it with a GameWeek
# fixture = Fixture(game_week_id=1)  # Replace 1 with the desired game week ID
# game_week = GameWeek.query.filter_by(game_week_number=1).first()  # Replace 1 with the desired game week number
# fixture.game_week_ref = game_week
# db.session.add(fixture)
# db.session.commit()
