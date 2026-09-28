from app import app
from models.hackathon import db, Hackathon
from datetime import datetime


REAL_HACKATHONS = [

    {
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
        "registration_url": "https://jagriti-hacks1.devpost.com/",
        "source_url": "https://jagriti-hacks1.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://compsphere12.devpost.com/",
        "source_url": "https://compsphere12.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://decentrahack-2-0.devpost.com/",
        "source_url": "https://decentrahack-2-0.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://hack2heal.devpost.com/",
        "source_url": "https://hack2heal.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://forgehacks-2026.devpost.com/",
        "source_url": "https://forgehacks-2026.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://next-gen-hackathon.devpost.com/",
        "source_url": "https://next-gen-hackathon.devpost.com/",
        "status": "Open"
    },

    {
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
        "registration_url": "https://indux-5-0-2026.devpost.com/",
        "source_url": "https://indux-5-0-2026.devpost.com/",
        "status": "Open"
    }
]


with app.app_context():

    added = 0
    skipped = 0

    for data in REAL_HACKATHONS:

        existing = Hackathon.query.filter_by(
            source_url=data["source_url"]
        ).first()

        if existing:
            print("⏭️ Already exists:", data["name"])
            skipped += 1
            continue

        hackathon = Hackathon(
            name=data["name"],
            organizer=data["organizer"],
            description=data["description"],
            registration_deadline=data["registration_deadline"],
            event_date=data["event_date"],
            location=data["location"],
            mode=data["mode"],
            prize_pool=data["prize_pool"],
            team_size=data["team_size"],
            eligibility=data["eligibility"],
            technologies=data["technologies"],
            registration_url=data["registration_url"],
            source_url=data["source_url"],
            status=data["status"],
            last_updated=datetime.utcnow()
        )

        db.session.add(hackathon)

        print("✅ Added:", data["name"])
        added += 1

    db.session.commit()

    print()
    print("=" * 60)
    print("🎉 REAL HACKATHONS ADDED")
    print("=" * 60)
    print("New hackathons:", added)
    print("Already existed:", skipped)
    print("=" * 60)