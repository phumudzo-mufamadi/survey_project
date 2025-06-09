import os
import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import func, cast, Integer
from models import db
from utils import calculate_age, save_response
from models import SurveyParticipant, SurveyResponse

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  f'sqlite:///{os.path.join(BASEDIR, "instance", "survey.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        full_names = request.form.get('full_names')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        dt = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        age = calculate_age(dt)
        contact_number = request.form.get('contact_number')
        # Save participant data to the database
        try:
            participant = SurveyParticipant(
                full_name=full_names,
                email=email,
                date_of_birth=dt,
                age=age,
                contact_number=contact_number
            )
            db.session.add(participant)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('You have already taken the survey with this email address.', 'error')
            return redirect(url_for('survey'))

        print(f"Participant {full_names} added with ID {participant.id}")
        # Save survey responses
        favorite_foods = request.form.getlist('favorite_foods')
        watch_movies = request.form.get('watch_movies')
        listen_radio = request.form.get('listen_radio')
        eat_out = request.form.get('eat_out')
        watch_tv = request.form.get('watch_tv')
        for food in favorite_foods:
            save_response(db, participant.id, 'favorite_food', food)

        save_response(db, participant.id, 'watch_movies', watch_movies)
        save_response(db, participant.id, 'listen_radio', listen_radio)
        save_response(db, participant.id, 'eat_out', eat_out)
        save_response(db, participant.id, 'watch_tv', watch_tv)
        flash('Survey submitted successfully!', 'success')
        return redirect(url_for('survey'))
    return render_template('survey.html')


@app.route('/results')
def results():
    total_surveys = SurveyParticipant.query.count()
    average_age = db.session.query(func.avg(SurveyParticipant.age)).scalar()
    max_age = db.session.query(func.max(SurveyParticipant.age)).scalar()
    min_age = db.session.query(func.min(SurveyParticipant.age)).scalar()
    pizza_total = SurveyResponse.query.filter(
        SurveyResponse.question=='favorite_food', SurveyResponse.answer=='Pizza').count()

    pasta_total = SurveyResponse.query.filter(
        SurveyResponse.question == 'favorite_food', SurveyResponse.answer == 'Pasta').count()

    papwors_total = SurveyResponse.query.filter(
        SurveyResponse.question == 'favorite_food', SurveyResponse.answer == 'Pap and Wors').count()

    pizza_pct = pizza_total / total_surveys * 100
    pasta_pct = pasta_total / total_surveys * 100
    papwors_pct = papwors_total / total_surveys * 100

    total_movies = (db.session.query(func.sum(cast(SurveyResponse.answer, Integer)))
                    .filter(SurveyResponse.question=='watch_movies').scalar())
    total_radio = (db.session.query(func.sum(cast(SurveyResponse.answer, Integer)))
                    .filter(SurveyResponse.question == 'listen_radio').scalar())
    total_eat_out = (db.session.query(func.sum(cast(SurveyResponse.answer, Integer)))
                    .filter(SurveyResponse.question == 'eat_out').scalar())
    total_watch_tv = (db.session.query(func.sum(cast(SurveyResponse.answer, Integer)))
                    .filter(SurveyResponse.question == 'watch_tv').scalar())

    avg_movies = total_movies / total_surveys
    avg_radio = total_radio / total_surveys
    avg_eatout = total_eat_out / total_surveys
    avg_watchtv = total_watch_tv / total_surveys

    return render_template(
        'results.html',
        total_surveys=total_surveys,
        average_age=average_age,
        max_age=max_age,
        min_age=min_age,
        pizza_pct=round(pizza_pct, 1),
        pasta_pct=round(pasta_pct, 1),
        papwors_pct=round(papwors_pct, 1),
        avg_movies=round(avg_movies, 1),
        avg_radio=round(avg_radio, 1),
        avg_eatout=round(avg_eatout, 1),
        avg_watchtv=round(avg_watchtv,1),
    )



if __name__ == '__main__':
    app.run(debug=True)
