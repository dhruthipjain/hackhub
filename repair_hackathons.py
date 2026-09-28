from app import app
from models.hackathon import db, Hackathon
from datetime import datetime


CORRECT_DATA = {

    "https://jagriti-hacks1.devpost.com/": {
        "name": "Jāgriti Hacks",
        "organizer": "Jāgriti Technologies PVT LTD",
        "description": "Ideas For a Safer Tomorrow",
        "registration_deadline": "29 September 2026",
        "event_date": "26 September - 12 October 2026",
        "location": "Online",
        "mode": "Online",
        "prize_pool": "$850",
        "team_size": "4 members",
        "eligibility": "Students only; specific countries/territories",
        "technologies": "Cybersecurity, DevOps, Machine Learning/AI",
        "status": "Open"
    },

    "https://compsphere12.devpost.com/": {
        "name": "COMPSPHERE 12",
        "organizer": "President University",
        "description": "Connect The Ideas, Create The Future",
        "registration_deadline": "1 October 2026",
        "event_date": "9 September - 11 October 2026",
        "location": "Online",
        "mode": "Online",
        "prize_pool": "$1,247",
        "team_size": "3 members",
        "eligibility": "Students aged 15-25",
        "technologies": "Blockchain, Machine Learning/AI, Cybersecurity",
        "status": "Open"
    },

    "https://decentrahack-2-0.devpost.com/": {
        "name": "DecentraHack 2.0",
        "organizer": "Pimpri Chinchwad College of Engineering",
        "description": "Build what matters. Prove why it needs to exist.",
        "registration_deadline": "30 September 2026",
        "event_date": "20 September - 9 October 2026",
        "location": "Pune, India",
        "mode": "Online + Offline Final",
        "prize_pool": "₹15,000+",
        "team_size": "2-4 members",
        "eligibility": "College students in second year and above",
        "technologies": "Agentic AI, Blockchain/Web3, Open Source",
        "status": "Open"
    },

    "https://hack2heal.devpost.com/": {
        "name": "Hack2Heal 2.0 - Global Healthcare Innovation Hackathon",
        "organizer": "Institute of Engineering & Management",
        "description": "Build anything. Solve for health. A global online healthcare innovation hackathon.",
        "registration_deadline": "30 September 2026",
        "event_date": "September 2026",
        "location": "Online",
        "mode": "Online",
        "prize_pool": "$100+",
        "team_size": "Individual or team",
        "eligibility": "College/university students worldwide",
        "technologies": "Health, Machine Learning/AI, Biotechnology, Data Science",
        "status": "Open"
    },

    "https://forgehacks-2026.devpost.com/": {
        "name": "ForgeHacks Online 2026",
        "organizer": "ForgeHacks",
        "description": "A student hackathon focused on forging AI solutions that solve real-world challenges.",
        "registration_deadline": "10 October 2026",
        "event_date": "3 October - 10 October 2026",
        "location": "Online",
        "mode": "Online",
        "prize_pool": "$410,491",
        "team_size": "1-4 participants",
        "eligibility": "Current high school, undergraduate and graduate students worldwide",
        "technologies": "Artificial Intelligence",
        "status": "Open"
    },

    "https://next-gen-hackathon.devpost.com/": {
        "name": "Next Gen Hackathon 2026 - Bengaluru",
        "organizer": "RAAIF",
        "description": "NextGenExpo'26 brings students, developers, engineers, innovators and startups together for technology challenges.",
        "registration_deadline": "23 October 2026",
        "event_date": "1 September - 23 October 2026",
        "location": "Bengaluru, India",
        "mode": "Offline",
        "prize_pool": "₹50,000",
        "team_size": "2-4 members",
        "eligibility": "Open to eligible participants; see official rules",
        "technologies": "Machine Learning/AI",
        "status": "Open"
    },

    "https://indux-5-0-2026.devpost.com/": {
        "name": "INDUX 5.0-2026",
        "organizer": "INDUX",
        "description": "AI FOR REAL-WORLD IMPACT",
        "registration_deadline": "15 October 2026",
        "event_date": "14 September - 3 November 2026",
        "location": "Gwalior, India",
        "mode": "Online + Offline",
        "prize_pool": "Check official source",
        "team_size": "Team based",
        "eligibility": "Students and young innovators from India and abroad",
        "technologies": "Artificial Intelligence",
        "status": "Open"
    }
}


with app.app_context():

    repaired = 0

    for url, data in CORRECT_DATA.items():

        hackathon = Hackathon.query.filter_by(
            source_url=url
        ).first()

        if not hackathon:
            print("⚠️ Not found:", url)
            continue

        for field, value in data.items():
            setattr(hackathon, field, value)

        hackathon.last_updated = datetime.utcnow()

        print("🔧 Repaired:", hackathon.name)

        repaired += 1

    db.session.commit()

    print()
    print("=" * 60)
    print("✅ HACKATHON DATA REPAIRED")
    print("=" * 60)
    print("Repaired:", repaired)
    print("=" * 60)