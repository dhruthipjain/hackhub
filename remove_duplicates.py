from app import app
from models.hackathon import db, Hackathon


with app.app_context():

    hackathons = Hackathon.query.order_by(Hackathon.id).all()

    seen = set()
    deleted = 0

    for hackathon in hackathons:

        key = (
            hackathon.name.strip().lower(),
            hackathon.organizer.strip().lower()
        )

        if key in seen:

            db.session.delete(hackathon)
            deleted += 1

        else:

            seen.add(key)


    db.session.commit()

    print(f"Removed {deleted} duplicate hackathons.")