from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import subprocess
import sys

from models.hackathon import db, Hackathon


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hackhub.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_deadline(hackathon):

    try:
        return datetime.strptime(
            hackathon.registration_deadline,
            "%d %B %Y"
        )

    except Exception:
        return datetime.max


def get_last_updated():
    try:
        with open("refresh_time.txt", "r", encoding="utf-8") as file:
            refresh_time = file.read().strip()

        if refresh_time:
            return refresh_time

    except FileNotFoundError:
        pass

    return "Not updated yet"


def is_unknown(value):

    if not value:
        return True

    value = str(value).strip().lower()

    return value in [
        "check official source",
        "not available",
        "unknown",
        "none",
        "null"
    ]


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    search = request.args.get(
        "search",
        ""
    ).strip()

    selected_filter = request.args.get(
        "filter",
        "all"
    ).strip().lower()

    # Get all records
    query = Hackathon.query

    hackathons = query.all()

    # ========================================================
    # SEARCH
    # ========================================================

    if search:

        search_lower = search.lower()

        filtered_hackathons = []

        for hackathon in hackathons:

            searchable_text = " ".join([
                hackathon.name or "",
                hackathon.organizer or "",
                hackathon.description or "",
                hackathon.mode or "",
                hackathon.location or "",
                hackathon.technologies or ""
            ]).lower()

            if search_lower in searchable_text:

                filtered_hackathons.append(
                    hackathon
                )

        hackathons = filtered_hackathons

    # ========================================================
    # FILTERS
    # ========================================================

    if selected_filter not in [
        "",
        "all"
    ]:

        filtered_hackathons = []

        for hackathon in hackathons:

            mode = (
                hackathon.mode or ""
            ).lower()

            technologies = (
                hackathon.technologies or ""
            ).lower()

            description = (
                hackathon.description or ""
            ).lower()

            combined = (
                mode
                + " "
                + technologies
                + " "
                + description
            )

            should_include = False

            # Online
            if selected_filter == "online":

                if "online" in mode:

                    should_include = True

            # Offline
            elif selected_filter == "offline":

                if (
                    "offline" in mode
                    or "in-person" in mode
                    or "in person" in mode
                ):

                    should_include = True

            # Hybrid
            elif selected_filter == "hybrid":

                if "hybrid" in mode:

                    should_include = True

            # AI / ML
            elif selected_filter in [
                "ai",
                "ai/ml",
                "aiml",
                "ai-ml"
            ]:

                keywords = [
                    "artificial intelligence",
                    "machine learning",
                    "ai/ml",
                    "ai",
                    "generative ai",
                    "deep learning"
                ]

                for keyword in keywords:

                    if keyword in combined:

                        should_include = True
                        break

            # Web
            elif selected_filter == "web":

                keywords = [
                    "web",
                    "website",
                    "frontend",
                    "backend",
                    "full stack",
                    "full-stack"
                ]

                for keyword in keywords:

                    if keyword in combined:

                        should_include = True
                        break

            # Cybersecurity
            elif selected_filter in [
                "cybersecurity",
                "cyber security"
            ]:

                keywords = [
                    "cybersecurity",
                    "cyber security",
                    "security",
                    "ethical hacking",
                    "penetration testing"
                ]

                for keyword in keywords:

                    if keyword in combined:

                        should_include = True
                        break

            if should_include:

                filtered_hackathons.append(
                    hackathon
                )

        hackathons = filtered_hackathons

    # ========================================================
    # SORT BY DEADLINE
    # ========================================================

    hackathons.sort(
        key=parse_deadline
    )

    # ========================================================
    # CLOSING SOON
    # ========================================================

    closing_soon = []

    now = datetime.now()

    for hackathon in hackathons:

        deadline = parse_deadline(
            hackathon
        )

        if deadline == datetime.max:
            continue

        difference = (
            deadline - now
        ).total_seconds()

        # Events closing within 30 days
        if 0 < difference <= (
            30 * 24 * 60 * 60
        ):

            closing_soon.append(
                hackathon
            )

    # Sort closing soon
    closing_soon.sort(
        key=parse_deadline
    )

    # ========================================================
    # LAST UPDATED
    # ========================================================

    last_updated = get_last_updated()

    # ========================================================
    # RENDER HOME
    # ========================================================

    return render_template(
        "index.html",
        hackathons=hackathons,
        closing_soon=closing_soon,
        search=search,
        filter=selected_filter,
        last_updated=last_updated
    )


# ============================================================
# HACKATHON DETAILS
# ============================================================

@app.route(
    "/hackathon/<int:hackathon_id>"
)
def hackathon_details(
    hackathon_id
):

    hackathon = Hackathon.query.get_or_404(
        hackathon_id
    )

    return render_template(
        "hackathon.html",
        hackathon=hackathon
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
def admin():

    hackathons = (
        Hackathon.query
        .order_by(Hackathon.id.desc())
        .all()
    )

    return render_template(
        "admin.html",
        hackathons=hackathons,
        last_updated=get_last_updated()
    )


# ============================================================
# ADMIN - UPDATE HACKATHONS
# ============================================================


@app.route("/admin/update", methods=["POST"])
def admin_update():

    message = ""

    try:

        script_path = "import_discovered_hackathons.py"

        result = subprocess.run(
            [
                sys.executable,
                script_path
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
            )

        # Print importer output in terminal
        print()
        print("=" * 60)
        print("HACKHUB ADMIN UPDATE")
        print("=" * 60)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        print("=" * 60)

        # If importer succeeded
        if result.returncode == 0:

            # Record the actual refresh time
            current_time = datetime.now().strftime(
                "%d %B %Y, %I:%M %p"
            )

            with open(
                "refresh_time.txt",
                "w",
                encoding="utf-8"
            ) as file:

                file.write(current_time)

            message = (
                "✅ Hackathons updated successfully!"
            )

        else:

            message = (
                "❌ Hackathon update failed. "
                "Check the terminal for details."
            )

    except Exception as error:

        message = (
            "❌ Update failed: "
            + str(error)
        )

        print(
            "Admin update error:",
            error
        )

    # Reload hackathons after update
    hackathons = (
        Hackathon.query
        .order_by(Hackathon.id.desc())
        .all()
    )

    return render_template(
        "admin.html",
        hackathons=hackathons,
        update_message=message,
        last_updated=get_last_updated()
    )
# ============================================================
# ADD HACKATHON
# ============================================================

@app.route(
    "/admin/add",
    methods=["GET", "POST"]
)
def add_hackathon():

    if request.method == "POST":

        hackathon = Hackathon(

            name=request.form.get(
                "name",
                ""
            ).strip(),

            organizer=request.form.get(
                "organizer",
                ""
            ).strip(),

            description=request.form.get(
                "description",
                ""
            ).strip(),

            registration_deadline=request.form.get(
                "registration_deadline",
                ""
            ).strip(),

            event_date=request.form.get(
                "event_date",
                ""
            ).strip(),

            location=request.form.get(
                "location",
                ""
            ).strip(),

            mode=request.form.get(
                "mode",
                ""
            ).strip(),

            prize_pool=request.form.get(
                "prize_pool",
                ""
            ).strip(),

            team_size=request.form.get(
                "team_size",
                ""
            ).strip(),

            eligibility=request.form.get(
                "eligibility",
                ""
            ).strip(),

            technologies=request.form.get(
                "technologies",
                ""
            ).strip(),

            registration_url=request.form.get(
                "registration_url",
                ""
            ).strip(),

            source_url=request.form.get(
                "source_url",
                ""
            ).strip(),

            status=request.form.get(
                "status",
                "Open"
            ).strip(),

            last_updated=datetime.utcnow()
        )

        db.session.add(
            hackathon
        )

        db.session.commit()

        return redirect(
            url_for("admin")
        )

    return render_template(
        "add_hackathon.html"
    )


# ============================================================
# EDIT HACKATHON
# ============================================================

@app.route(
    "/admin/edit/<int:hackathon_id>",
    methods=["GET", "POST"]
)
def edit_hackathon(
    hackathon_id
):

    hackathon = Hackathon.query.get_or_404(
        hackathon_id
    )

    if request.method == "POST":

        hackathon.name = request.form.get(
            "name",
            ""
        ).strip()

        hackathon.organizer = request.form.get(
            "organizer",
            ""
        ).strip()

        hackathon.description = request.form.get(
            "description",
            ""
        ).strip()

        hackathon.registration_deadline = request.form.get(
            "registration_deadline",
            ""
        ).strip()

        hackathon.event_date = request.form.get(
            "event_date",
            ""
        ).strip()

        hackathon.location = request.form.get(
            "location",
            ""
        ).strip()

        hackathon.mode = request.form.get(
            "mode",
            ""
        ).strip()

        hackathon.prize_pool = request.form.get(
            "prize_pool",
            ""
        ).strip()

        hackathon.team_size = request.form.get(
            "team_size",
            ""
        ).strip()

        hackathon.eligibility = request.form.get(
            "eligibility",
            ""
        ).strip()

        hackathon.technologies = request.form.get(
            "technologies",
            ""
        ).strip()

        hackathon.registration_url = request.form.get(
            "registration_url",
            ""
        ).strip()

        hackathon.source_url = request.form.get(
            "source_url",
            ""
        ).strip()

        hackathon.status = request.form.get(
            "status",
            "Open"
        ).strip()

        hackathon.last_updated = datetime.utcnow()

        db.session.commit()

        return redirect(
            url_for("admin")
        )

    return render_template(
        "edit_hackathon.html",
        hackathon=hackathon
    )


# ============================================================
# DELETE HACKATHON
# ============================================================

@app.route(
    "/admin/delete/<int:hackathon_id>",
    methods=["POST"]
)
def delete_hackathon(
    hackathon_id
):

    hackathon = Hackathon.query.get_or_404(
        hackathon_id
    )

    db.session.delete(
        hackathon
    )

    db.session.commit()

    return redirect(
        url_for("admin")
    )


# ============================================================
# SIMPLE ABOUT PAGE
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )