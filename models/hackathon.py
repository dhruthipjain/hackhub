from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Hackathon(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    organizer = db.Column(
        db.String(200)
    )

    description = db.Column(
        db.Text
    )

    registration_deadline = db.Column(
        db.String(100)
    )

    event_date = db.Column(
        db.String(100)
    )

    location = db.Column(
        db.String(200)
    )

    mode = db.Column(
        db.String(50)
    )

    prize_pool = db.Column(
        db.String(100)
    )

    team_size = db.Column(
        db.String(100)
    )

    eligibility = db.Column(
        db.Text
    )

    technologies = db.Column(
        db.String(500)
    )

    registration_url = db.Column(
        db.String(500)
    )

    source_url = db.Column(
        db.String(500)
    )

    status = db.Column(
        db.String(50),
        default="Open"
    )

    last_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )