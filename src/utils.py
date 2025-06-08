from datetime import date
from models import SurveyResponse

def calculate_age(date_of_birth):
    today = date.today()
    age = today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )
    return age

def save_response(db, participant_id, field, value):
    response = SurveyResponse(
        participant_id=participant_id,
        question=field,
        answer=value,
        submission_date=date.today()
    )
    db.session.add(response)
    db.session.commit()
    print(f"Response saved for participant {participant_id}: {field} = {value}")

