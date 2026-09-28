from app import app
from models.hackathon import db, Hackathon

BAD_URLS = [
    "https://example.com",
    "http://127.0.0.1:5000"
]

with app.app_context():

    deleted = 0

    records = Hackathon.query.all()

    for hackathon in records:

        if hackathon.source_url in BAD_URLS:

            print("🗑️ Removing:", hackathon.name)

            db.session.delete(hackathon)
            deleted += 1

    db.session.commit()

    print()
    print("=" * 50)
    print("DEMO RECORD CLEANUP COMPLETE")
    print("=" * 50)
    print("Deleted:", deleted)
    print("=" * 50)