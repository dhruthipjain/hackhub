from app import app
from models.hackathon import db
from sqlalchemy import inspect, text


with app.app_context():

    inspector = inspect(db.engine)

    columns = [
        column["name"]
        for column in inspector.get_columns("hackathon")
    ]

    print("Current columns:")
    print(columns)

    if "last_updated" not in columns:

        print("Adding last_updated column...")

        db.session.execute(
            text(
                "ALTER TABLE hackathon "
                "ADD COLUMN last_updated DATETIME"
            )
        )

        db.session.commit()

        print("✅ last_updated column added successfully!")

    else:

        print("✅ last_updated already exists!")
