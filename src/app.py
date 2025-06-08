import os
import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import func
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
    return render_template(
        'results.html',
        total_surveys=total_surveys,
        average_age=average_age,
        max_age=max_age,
        min_age=min_age,
    )


if __name__ == '__main__':
    app.run(debug=True)
