# ============================================================
# HACKHUB - AUTOMATIC HACKATHON DISCOVERY
# ============================================================

import sys

# ------------------------------------------------------------
# FORCE UTF-8 OUTPUT ON WINDOWS
# ------------------------------------------------------------

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

import requests
import re

from datetime import datetime

from app import app
from models.hackathon import db, Hackathon


# ============================================================
# CONFIGURATION
# ============================================================

FEED_URL = "https://hackathonsboard.netlify.app/events.json"

REQUEST_TIMEOUT = 30

REFRESH_FILE = "refresh_time.txt"


# ============================================================
# HTTP HEADERS
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*"
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    """
    Convert any value into clean text.
    """

    if value is None:
        return ""

    if isinstance(value, (list, tuple)):

        values = []

        for item in value:

            text = clean_text(item)

            if text:
                values.append(text)

        return ", ".join(values)

    if isinstance(value, dict):

        # Prefer common text fields
        for key in [
            "name",
            "title",
            "text",
            "value",
            "description",
            "label"
        ]:

            if key in value:

                text = clean_text(
                    value[key]
                )

                if text:
                    return text

        return ""

    text = str(value)

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Decode common HTML entities
    replacements = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&nbsp;": " "
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def first_value(data, keys):
    """
    Find the first useful value from a dictionary.
    """

    if not isinstance(data, dict):
        return ""

    for key in keys:

        if key in data:

            value = clean_text(
                data[key]
            )

            if value:
                return value

    return ""


def find_nested_value(data, keys):
    """
    Search nested dictionaries/lists for a value.
    """

    if isinstance(data, dict):

        # Check current level first
        value = first_value(
            data,
            keys
        )

        if value:
            return value

        # Search nested values
        for child in data.values():

            result = find_nested_value(
                child,
                keys
            )

            if result:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_nested_value(
                item,
                keys
            )

            if result:
                return result

    return ""


def normalize_url(url):
    """
    Normalize URLs for duplicate checking.
    """

    if not url:
        return ""

    url = url.strip()

    if not url.startswith("http"):

        url = "https://" + url

    url = url.rstrip("/")

    return url.lower()


def is_devpost_url(url):
    """
    Accept only public Devpost hackathon URLs.
    """

    if not url:
        return False

    url_lower = url.lower()

    return (
        "devpost.com" in url_lower
        and "info.devpost.com" not in url_lower
    )


def is_bad_page(name, url, description):
    """
    Prevent obvious Devpost marketing/legal pages
    from entering the hackathon database.
    """

    text = (
        clean_text(name)
        + " "
        + clean_text(url)
        + " "
        + clean_text(description)
    ).lower()

    bad_keywords = [

        # Devpost company pages
        "devpost blog",
        "customer stories",
        "contact devpost",
        "contact us",
        "about devpost",
        "privacy policy",
        "terms of service",
        "california consumer privacy act",

        # Marketing pages
        "get a demo",
        "webinar",
        "webinars",
        "product adoption",
        "private hackathons",
        "real ai adoption",
        "leading hackathon platform",
        "platform behind",
        "deepening engagement",
        "deepen engagement",

        # Guides/resources
        "hackathon planning guides",
        "hackathon planning guide",
        "hackathon guides",
        "help us inspire developers",
        "resources",

        # Navigation
        "/legal/",
        "/privacy",
        "/terms",
        "/contact",
        "/about"
    ]

    for keyword in bad_keywords:

        if keyword in text:

            return True

    return False


def looks_like_hackathon(name, description, url):
    """
    Check whether a record appears to be a real hackathon.
    """

    combined = (
        clean_text(name)
        + " "
        + clean_text(description)
        + " "
        + clean_text(url)
    ).lower()

    hackathon_keywords = [

        "hackathon",
        "hack",
        "hack day",
        "coding challenge",
        "code challenge",
        "innovation challenge",
        "buildathon",
        "devpost"
    ]

    for keyword in hackathon_keywords:

        if keyword in combined:

            return True

    # A Devpost subdomain is usually enough
    if ".devpost.com" in url.lower():

        return True

    return False


# ============================================================
# DATE FUNCTIONS
# ============================================================

def parse_date_value(value):
    """
    Convert common date formats into datetime.
    """

    if not value:
        return None

    value = clean_text(value)

    if not value:
        return None

    # Remove timezone suffixes
    cleaned = value.replace(
        "Z",
        ""
    ).strip()

    formats = [

        "%Y-%m-%d",

        "%Y-%m-%dT%H:%M:%S",

        "%Y-%m-%dT%H:%M:%S.%f",

        "%Y-%m-%d %H:%M:%S",

        "%d %B %Y",

        "%d %b %Y",

        "%B %d, %Y",

        "%b %d, %Y",

        "%d/%m/%Y",

        "%m/%d/%Y"
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                cleaned,
                fmt
            )

        except ValueError:

            pass

    # Try ISO parser
    try:

        return datetime.fromisoformat(
            cleaned
        )

    except Exception:

        pass

    return None


def format_date(value):
    """
    Return dates in HackHub's format.
    """

    parsed = parse_date_value(
        value
    )

    if parsed:

        return parsed.strftime(
            "%d %B %Y"
        )

    return ""


def extract_deadline(event):
    """
    Try several possible deadline fields.
    """

    value = first_value(
        event,
        [
            "registration_deadline",
            "registrationDeadline",
            "deadline",
            "registrationEnd",
            "registration_end",
            "endDate",
            "end_date",
            "submission_deadline",
            "submissionDeadline"
        ]
    )

    if value:

        return format_date(
            value
        )

    # Search nested data
    value = find_nested_value(
        event,
        [
            "registration_deadline",
            "registrationDeadline",
            "deadline",
            "registrationEnd",
            "registration_end"
        ]
    )

    if value:

        return format_date(
            value
        )

    return ""


# ============================================================
# EVENT DATE
# ============================================================

def extract_event_date(event):

    start = first_value(
        event,
        [
            "startDate",
            "start_date",
            "event_date",
            "eventDate",
            "date",
            "start"
        ]
    )

    end = first_value(
        event,
        [
            "endDate",
            "end_date",
            "end"
        ]
    )

    start_formatted = format_date(
        start
    )

    end_formatted = format_date(
        end
    )

    if start_formatted and end_formatted:

        return (
            start_formatted
            + " - "
            + end_formatted
        )

    if start_formatted:

        return start_formatted

    if end_formatted:

        return end_formatted

    return ""


# ============================================================
# STATUS
# ============================================================

def extract_status(event, deadline):
    """
    Determine registration status.
    """

    raw_status = str(
        first_value(
            event,
            [
                "status",
                "registration_status",
                "registrationStatus"
            ]
        )
        or ""
    ).lower()

    if raw_status in [
        "open",
        "active",
        "ongoing",
        "upcoming"
    ]:

        return "Open"

    if raw_status in [
        "closed",
        "ended",
        "completed",
        "expired"
    ]:

        return "Closed"

    # If we have a future deadline,
    # registration is probably open.
    parsed_deadline = parse_date_value(
        deadline
    )

    if parsed_deadline:

        if parsed_deadline >= datetime.now():

            return "Open"

        return "Closed"

    return "Check official source"


# ============================================================
# MODE
# ============================================================

def extract_mode(event):

    mode = first_value(
        event,
        [
            "mode",
            "format",
            "type"
        ]
    )

    if mode:

        mode_lower = mode.lower()

        if "hybrid" in mode_lower:

            return "Hybrid"

        if "offline" in mode_lower:
            return "Offline"

        if "in-person" in mode_lower:
            return "Offline"

        if "in person" in mode_lower:
            return "Offline"

        if "online" in mode_lower:

            return "Online"

        return mode

    # Check boolean fields
    online = first_value(
        event,
        [
            "online",
            "is_online"
        ]
    ).lower()

    if online in [
        "true",
        "yes",
        "1"
    ]:

        return "Online"

    return "Online"


# ============================================================
# LOCATION
# ============================================================

def extract_location(event):

    location = first_value(
        event,
        [
            "location",
            "city",
            "venue",
            "address"
        ]
    )

    if location:

        return location

    return "Online"


# ============================================================
# PRIZE
# ============================================================

def extract_prize(event):

    prize = first_value(
        event,
        [
            "prize_pool",
            "prizePool",
            "prize",
            "prizes",
            "total_prize",
            "totalPrize",
            "cash_prize",
            "cashPrize"
        ]
    )

    if prize:

        return prize

    return ""


# ============================================================
# ORGANIZER
# ============================================================

def extract_organizer(event):

    organizer = first_value(
        event,
        [
            "organizer",
            "organiser",
            "organization",
            "organisation",
            "host",
            "company"
        ]
    )

    if organizer:

        return organizer

    return ""


# ============================================================
# DESCRIPTION
# ============================================================

def extract_description(event):

    description = first_value(
        event,
        [
            "description",
            "summary",
            "short_description",
            "shortDescription",
            "details"
        ]
    )

    if description:

        return description[:3000]

    return (
        "Hackathon discovered automatically from "
        "the HackHub public hackathon feed. "
        "Visit the official Devpost page for complete "
        "rules, eligibility and deadline."
    )


# ============================================================
# TECHNOLOGIES / THEMES
# ============================================================

def extract_themes(event):

    themes = first_value(
        event,
        [
            "themes",
            "theme",
            "tags",
            "technologies",
            "technology",
            "categories",
            "category"
        ]
    )

    if themes:

        return themes[:500]

    return ""


# ============================================================
# ELIGIBILITY
# ============================================================

def extract_eligibility(event):

    eligibility = first_value(
        event,
        [
            "eligibility",
            "who_can_participate",
            "whoCanParticipate",
            "participants"
        ]
    )

    if eligibility:

        return eligibility[:2000]

    return ""


# ============================================================
# TEAM SIZE
# ============================================================

def extract_team_size(event):

    team_size = first_value(
        event,
        [
            "team_size",
            "teamSize",
            "teams",
            "team"
        ]
    )

    if team_size:

        return team_size[:200]

    return ""


# ============================================================
# URL
# ============================================================

def extract_url(event):

    url = first_value(
        event,
        [
            "url",
            "link",
            "event_url",
            "eventUrl",
            "devpost_url",
            "devpostUrl"
        ]
    )

    return normalize_url(
        url
    )


# ============================================================
# NAME
# ============================================================

def extract_name(event):

    name = first_value(
        event,
        [
            "name",
            "title",
            "event_name",
            "eventName"
        ]
    )

    return name[:200]


# ============================================================
# CONVERT EVENT INTO HACKHUB DATA
# ============================================================

def create_hackathon_data(event):

    name = extract_name(
        event
    )

    url = extract_url(
        event
    )

    description = extract_description(
        event
    )

    organizer = extract_organizer(
        event
    )

    deadline = extract_deadline(
        event
    )

    event_date = extract_event_date(
        event
    )

    prize = extract_prize(
        event
    )

    mode = extract_mode(
        event
    )

    location = extract_location(
        event
    )

    themes = extract_themes(
        event
    )

    eligibility = extract_eligibility(
        event
    )

    team_size = extract_team_size(
        event
    )

    status = extract_status(
        event,
        deadline
    )

    return {

        "name": name,

        "organizer": (
            organizer
            or "Check official source"
        ),

        "description": description,

        "registration_deadline": (
            deadline
            or "Check official source"
        ),

        "event_date": (
            event_date
            or "Check official source"
        ),

        "location": (
            location
            or "Check official source"
        ),

        "mode": (
            mode
            or "Check official source"
        ),

        "prize_pool": (
            prize
            or "Check official source"
        ),

        "team_size": (
            team_size
            or "Check official source"
        ),

        "eligibility": (
            eligibility
            or "Check official source"
        ),

        "technologies": (
            themes
            or "Check official source"
        ),

        "registration_url": url,

        "source_url": url,

        "status": status
    }


# ============================================================
# DOWNLOAD FEED
# ============================================================

def download_feed():

    print()
    print("=" * 60)
    print("HACKHUB AUTOMATIC HACKATHON DISCOVERY")
    print("=" * 60)

    print(
        "Downloading public hackathon feed..."
    )

    try:

        response = requests.get(
            FEED_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        print(
            "Feed downloaded successfully."
        )

        return data

    except Exception as error:

        print(
            "ERROR: Could not download feed."
        )

        print(
            str(error)
        )

        return None


# ============================================================
# EXTRACT EVENTS FROM JSON
# ============================================================

def extract_events(data):

    if data is None:

        return []

    # Direct list
    if isinstance(data, list):

        return data

    # Common wrapper names
    if isinstance(data, dict):

        for key in [
            "events",
            "hackathons",
            "data",
            "results",
            "items"
        ]:

            value = data.get(
                key
            )

            if isinstance(value, list):

                return value

    # Recursive fallback
    if isinstance(data, dict):

        for value in data.values():

            if isinstance(value, list):

                if value and isinstance(
                    value[0],
                    dict
                ):

                    return value

    return []


# ============================================================
# EXISTING RECORD CHECK
# ============================================================

def find_existing(url, name):

    normalized_url = normalize_url(
        url
    )

    # First check source URL
    if normalized_url:

        records = Hackathon.query.all()

        for record in records:

            existing_url = normalize_url(
                record.source_url
            )

            if existing_url == normalized_url:

                return record

    # Then check name
    if name:

        record = (
            Hackathon.query
            .filter(
                db.func.lower(
                    Hackathon.name
                )
                == name.lower()
            )
            .first()
        )

        if record:

            return record

    return None


# ============================================================
# SAFE FIELD UPDATE
# ============================================================

def update_if_better(
    record,
    field,
    new_value
):

    if not new_value:

        return False

    new_value = clean_text(
        new_value
    )

    if not new_value:

        return False

    old_value = getattr(
        record,
        field,
        ""
    )

    old_text = clean_text(
        old_value
    )

    # Don't replace good information
    # with "Check official source"
    if (
        new_value == "Check official source"
        and old_text
        and old_text != "Check official source"
    ):

        return False

    if old_text == new_value:

        return False

    setattr(
        record,
        field,
        new_value
    )

    return True


# ============================================================
# IMPORT EVENTS
# ============================================================

def import_events(events):

    added = 0
    updated = 0
    skipped = 0
    failed = 0

    print()
    print("=" * 60)
    print(
        "PROCESSING EVENTS:",
        len(events)
    )
    print("=" * 60)

    for index, event in enumerate(
        events,
        start=1
    ):

        try:

            if not isinstance(
                event,
                dict
            ):

                skipped += 1
                continue

            name = extract_name(
                event
            )

            url = extract_url(
                event
            )

            description = extract_description(
                event
            )

            # Must have a name
            if not name:

                skipped += 1
                continue

            # Must have a Devpost URL
            if not is_devpost_url(
                url
            ):

                skipped += 1
                continue

            # Reject obvious non-hackathon pages
            if is_bad_page(
                name,
                url,
                description
            ):

                skipped += 1
                continue

            # Make sure it looks like a hackathon
            if not looks_like_hackathon(
                name,
                description,
                url
            ):

                skipped += 1
                continue

            data = create_hackathon_data(
                event
            )

            existing = find_existing(
                data["source_url"],
                data["name"]
            )

            if existing:

                changed = False

                fields = [
                    "name",
                    "organizer",
                    "description",
                    "registration_deadline",
                    "event_date",
                    "location",
                    "mode",
                    "prize_pool",
                    "team_size",
                    "eligibility",
                    "technologies",
                    "registration_url",
                    "source_url",
                    "status"
                ]

                for field in fields:

                    if update_if_better(
                        existing,
                        field,
                        data[field]
                    ):

                        changed = True

                if changed:

                    existing.last_updated = (
                        datetime.utcnow()
                    )

                    updated += 1

                    print(
                        "[UPDATED]",
                        data["name"]
                    )

                else:

                    skipped += 1

                continue

            # ------------------------------------------------
            # ADD NEW RECORD
            # ------------------------------------------------

            hackathon = Hackathon(
                name=data["name"],
                organizer=data["organizer"],
                description=data["description"],
                registration_deadline=data[
                    "registration_deadline"
                ],
                event_date=data["event_date"],
                location=data["location"],
                mode=data["mode"],
                prize_pool=data["prize_pool"],
                team_size=data["team_size"],
                eligibility=data["eligibility"],
                technologies=data["technologies"],
                registration_url=data[
                    "registration_url"
                ],
                source_url=data["source_url"],
                status=data["status"],
                last_updated=datetime.utcnow()
            )

            db.session.add(
                hackathon
            )

            added += 1

            print(
                "[ADDED]",
                data["name"]
            )

        except Exception as error:

            failed += 1

            print(
                "[FAILED]",
                str(error)
            )

    # Save database changes
    db.session.commit()

    return (
        added,
        updated,
        skipped,
        failed
    )


# ============================================================
# WRITE REFRESH TIME
# ============================================================

def write_refresh_time():

    current_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    try:

        with open(
            REFRESH_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                current_time
            )

        print()
        print(
            "Refresh time:",
            current_time
        )

    except Exception as error:

        print(
            "Warning: Could not write refresh time."
        )

        print(
            str(error)
        )


# ============================================================
# MAIN
# ============================================================

def main():

    data = download_feed()

    if data is None:

        print()
        print(
            "IMPORT FAILED"
        )

        return 1

    events = extract_events(
        data
    )

    if not events:

        print()
        print(
            "ERROR: No events found in feed."
        )

        return 1

    print()
    print(
        "Events received:",
        len(events)
    )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    with app.app_context():

        try:

            added, updated, skipped, failed = (
                import_events(events)
            )

            write_refresh_time()

            print()
            print("=" * 60)
            print("IMPORT COMPLETE")
            print("=" * 60)

            print(
                "New hackathons added:",
                added
            )

            print(
                "Existing hackathons updated:",
                updated
            )

            print(
                "Skipped:",
                skipped
            )

            print(
                "Failed:",
                failed
            )

            print(
                "Total in database:",
                Hackathon.query.count()
            )

            print("=" * 60)

            return 0

        except Exception as error:

            db.session.rollback()

            print()
            print("=" * 60)
            print("IMPORT FAILED")
            print("=" * 60)

            print(
                str(error)
            )

            print("=" * 60)

            return 1


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )