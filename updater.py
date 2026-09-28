import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app import app
from models.hackathon import db, Hackathon


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/153.0 Safari/537.36"
}


def get_page(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")

        print("❌ HTTP error:", response.status_code, url)

    except Exception as e:
        print("❌ Error opening:", url)
        print(e)

    return None


def clean_text(text):
    if not text:
        return ""

    return " ".join(text.split()).strip()


def extract_hackathon_details(hackathon):
    """
    Open the individual Devpost page and update
    information that can be reliably found.
    """

    url = hackathon.source_url

    if not url or "devpost.com" not in url:
        print("   ⚠️ Invalid Devpost URL")
        return False

    print("   🔎 Opening:", url)

    soup = get_page(url)

    if not soup:
        return False

    # -------------------------------------------------
    # PAGE TITLE
    # -------------------------------------------------

    title = soup.find("h1")

    if title:
        title_text = clean_text(title.get_text())

        if title_text:
            hackathon.name = title_text

    # -------------------------------------------------
    # MAIN PAGE TEXT
    # -------------------------------------------------

    page_text = clean_text(soup.get_text(" ", strip=True))

    # -------------------------------------------------
    # DESCRIPTION
    # -------------------------------------------------

    description = ""

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta_description:
        description = meta_description.get("content", "")

    description = clean_text(description)

    if description:
        hackathon.description = description

    # -------------------------------------------------
    # ORGANIZER
    # -------------------------------------------------

    organizer = ""

    organizer_label = soup.find(
        string=lambda text:
        text and "organized by" in text.lower()
    )

    if organizer_label:
        parent = organizer_label.parent

        if parent:
            organizer = clean_text(parent.get_text())

    if organizer:
        hackathon.organizer = organizer

    # -------------------------------------------------
    # PAGE INFORMATION
    # -------------------------------------------------

    # Search visible page text for common Devpost labels.

    lines = [
        clean_text(x.get_text(" ", strip=True))
        for x in soup.find_all(["p", "div", "span", "li"])
    ]

    lines = [x for x in lines if x]

    # -------------------------------------------------
    # MODE
    # -------------------------------------------------

    lower_page = page_text.lower()

    if "online | public" in lower_page:
        hackathon.mode = "Online"

    elif "online" in lower_page and "public" in lower_page:
        hackathon.mode = "Online"

    elif "in-person" in lower_page:
        hackathon.mode = "Offline"

    # -------------------------------------------------
    # PRIZE
    # -------------------------------------------------

    prize = ""

    for line in lines:

        lower = line.lower()

        if "in prizes" in lower:
            prize = line
            break

        if "prize" in lower and (
            "$" in line or
            "₹" in line or
            "€" in line
        ):
            prize = line
            break

    if prize:
        hackathon.prize_pool = prize

    # -------------------------------------------------
    # TEAM SIZE
    # -------------------------------------------------

    for line in lines:

        lower = line.lower()

        if "team size" in lower:
            hackathon.team_size = line
            break

        if "team required" in lower:
            hackathon.team_size = line
            break

    # -------------------------------------------------
    # ELIGIBILITY
    # -------------------------------------------------

    eligibility_parts = []

    for line in lines:

        lower = line.lower()

        if (
            "who can participate" in lower
            or "eligibility" in lower
            or "eligible" in lower
        ):
            eligibility_parts.append(line)

    if eligibility_parts:
        hackathon.eligibility = " ".join(
            eligibility_parts[:5]
        )

    # -------------------------------------------------
    # TECHNOLOGIES / TAGS
    # -------------------------------------------------

    tags = []

    for element in soup.select(
        ".software-list a, .challenge-tag, .tag"
    ):

        text = clean_text(element.get_text())

        if text and text not in tags:
            tags.append(text)

    if tags:
        hackathon.technologies = ", ".join(tags[:20])

    # -------------------------------------------------
    # LAST UPDATED
    # -------------------------------------------------

    hackathon.last_updated = datetime.utcnow()

    return True


def update_database():

    print()
    print("=" * 60)
    print("🚀 HACKHUB INDIVIDUAL PAGE UPDATER")
    print("=" * 60)

    with app.app_context():

        hackathons = Hackathon.query.all()

        if not hackathons:
            print("⚠️ No hackathons in database.")
            return

        updated = 0
        failed = 0

        for index, hackathon in enumerate(hackathons, start=1):

            print()
            print(
                f"[{index}/{len(hackathons)}] "
                f"{hackathon.name}"
            )

            if extract_hackathon_details(hackathon):
                updated += 1
                print("   ✅ Updated")

            else:
                failed += 1
                print("   ❌ Could not update")

        db.session.commit()

        print()
        print("=" * 60)
        print("✅ UPDATE COMPLETE")
        print("=" * 60)

        print("Updated:", updated)
        print("Failed:", failed)
        print("Total:", len(hackathons))

        print("=" * 60)


if __name__ == "__main__":
    update_database()