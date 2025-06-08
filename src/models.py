from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SurveyParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<SurveyParticipant {self.full_name}>'
    
class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('survey_participant.id'), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False)

    participant = db.relationship('SurveyParticipant', backref=db.backref('responses', lazy=True))

    def __repr__(self):
        return f'<SurveyResponse {self.id} by {self.participant.full_name}>'