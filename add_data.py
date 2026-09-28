from app import app
from models.hackathon import db, Hackathon


with app.app_context():

    hackathons = [

        {
            "name": "AI Innovation Hackathon",
            "organizer": "Tech Innovation Labs",
            "description": "Build innovative AI solutions for real-world problems.",
            "registration_deadline": "15 October 2026",
            "event_date": "20-22 October 2026",
            "location": "Online",
            "mode": "Online",
            "prize_pool": "₹5,00,000",
            "team_size": "2-4 members",
            "eligibility": "College students and beginners",
            "technologies": "Python, AI, Machine Learning",
            "registration_url": "https://example.com",
            "source_url": "https://example.com",
            "status": "Open"
        },

        {
            "name": "Future Web Hackathon",
            "organizer": "WebTech Community",
            "description": "Create innovative next-generation web applications.",
            "registration_deadline": "20 October 2026",
            "event_date": "25-27 October 2026",
            "location": "Bangalore",
            "mode": "Offline",
            "prize_pool": "₹2,00,000",
            "team_size": "2-5 members",
            "eligibility": "Students and developers",
            "technologies": "HTML, CSS, JavaScript, React",
            "registration_url": "https://example.com",
            "source_url": "https://example.com",
            "status": "Open"
        }
    ]


    for data in hackathons:

        existing = Hackathon.query.filter_by(
            name=data["name"],
            organizer=data["organizer"]
        ).first()

        if existing:
            print(f"Already exists: {data['name']}")

        else:
            hackathon = Hackathon(**data)

            db.session.add(hackathon)

            print(f"Added: {data['name']}")


    db.session.commit()

    print("Database update completed!")