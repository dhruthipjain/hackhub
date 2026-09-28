from app import app
from models.hackathon import db, Hackathon

BAD_IDS = [14, 15, 16, 17, 18, 19]

with app.app_context():

    deleted = 0

    for hackathon_id in BAD_IDS:
        hackathon = Hackathon.query.get(hackathon_id)

        if hackathon:
            print("🗑️ Removing:", hackathon.name)
            db.session.delete(hackathon)
            deleted += 1

    db.session.commit()

    print()
    print("=" * 50)
    print("CLEANUP COMPLETE")
    print("=" * 50)
    print("Deleted:", deleted)
    print("Kept your original 3 hackathons.")
    print("=" * 50)