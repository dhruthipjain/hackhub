import requests
from datetime import datetime
from urllib.parse import urlparse


FEED_URL = "https://hackathonsboard.netlify.app/events.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_events():

    print()
    print("=" * 60)
    print("🔎 HACKHUB DISCOVERY")
    print("=" * 60)

    try:

        response = requests.get(
            FEED_URL,
            headers=HEADERS,
            timeout=30
        )

        print("Feed status:", response.status_code)

        if response.status_code != 200:
            print("❌ Could not access feed")
            return []

        data = response.json()

        print("Feed downloaded successfully.")

        # Show available sources
        if isinstance(data, dict):

            sources = data.get("sources", [])

            print("Sources found:", len(sources))

            for source in sources:

                print(
                    " -",
                    source.get("name"),
                    "→",
                    source.get("count")
                )

        # Try common event locations
        events = []

        if isinstance(data, list):
            events = data

        elif isinstance(data, dict):

            if isinstance(data.get("events"), list):
                events = data["events"]

            elif isinstance(data.get("data"), list):
                events = data["data"]

            elif isinstance(data.get("hackathons"), list):
                events = data["hackathons"]

        print("Events received:", len(events))

        return events

    except Exception as e:

        print("❌ Error:", e)

        return []


def is_devpost_event(event):

    url = (
        event.get("url")
        or event.get("link")
        or event.get("website")
        or ""
    )

    if not url:
        return False

    try:

        parsed = urlparse(url)

        hostname = parsed.netloc.lower()

        # Accept normal Devpost event subdomains
        if hostname.endswith(".devpost.com"):
            return True

        return False

    except Exception:

        return False


def get_event_name(event):

    return (
        event.get("name")
        or event.get("title")
        or "Unnamed Hackathon"
    )


def get_event_url(event):

    return (
        event.get("url")
        or event.get("link")
        or event.get("website")
        or ""
    )


def main():

    events = get_events()

    if not events:

        print()
        print("❌ No events found.")
        return

    print()
    print("=" * 60)
    print("🎯 FILTERING DEVPOST EVENTS")
    print("=" * 60)

    devpost_events = []

    seen_urls = set()

    for event in events:

        if not isinstance(event, dict):
            continue

        if not is_devpost_event(event):
            continue

        url = get_event_url(event)

        if url in seen_urls:
            continue

        seen_urls.add(url)

        name = get_event_name(event)

        devpost_events.append(
            (name, url, event)
        )

    print(
        "Devpost events found:",
        len(devpost_events)
    )

    print()
    print("=" * 60)
    print("📋 DISCOVERED DEVPOST HACKATHONS")
    print("=" * 60)

    for number, (name, url, event) in enumerate(
        devpost_events[:30],
        start=1
    ):

        print()
        print(f"{number}. {name}")
        print(f"   🔗 {url}")

        # Display available fields
        for field in [
            "startDate",
            "endDate",
            "deadline",
            "prize",
            "location"
        ]:

            value = event.get(field)

            if value:
                print(
                    f"   {field}: {value}"
                )

    print()
    print("=" * 60)
    print(
        "Showing first 30 of",
        len(devpost_events)
    )
    print("=" * 60)

    print()
    print("⚠️ PREVIEW MODE")
    print("⚠️ DATABASE WAS NOT MODIFIED")
    print("=" * 60)


if __name__ == "__main__":
    main()