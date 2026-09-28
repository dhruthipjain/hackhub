from app import app
from models.hackathon import db, Hackathon


with app.app_context():

    records = Hackathon.query.all()

    fixed = 0

    for hackathon in records:

        deadline = (
            hackathon.registration_deadline
            or ""
        ).strip()

        organizer = (
            hackathon.organizer
            or ""
        ).strip()

        # Automatically imported records have
        # "Check official source" when the deadline
        # could not be verified.

        if deadline == "Check official source":

            if hackathon.status == "Open":

                hackathon.status = (
                    "Check official source"
                )

                print(
                    "🔧 Fixed:",
                    hackathon.name
                )

                fixed += 1

    db.session.commit()

    print()
    print("=" * 60)
    print("✅ REGISTRATION STATUS REPAIR COMPLETE")
    print("=" * 60)
    print("Records fixed:", fixed)
    print("=" * 60)