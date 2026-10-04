# 🚀 HackHub

### Automatic Hackathon Discovery Platform

HackHub is a web-based platform that helps students discover upcoming hackathons in one place.

Instead of searching through multiple websites, students can use HackHub to find hackathons, check deadlines, explore opportunities, and visit the official registration page.

The platform also includes an automatic hackathon discovery system that periodically retrieves hackathon information and updates the database.

---

## ✨ Features

### 🔎 Hackathon Discovery
- Browse upcoming hackathons in one place
- Search hackathons by name or keyword
- View hackathon information through dedicated cards

### 🎯 Smart Filtering
Filter hackathons based on:
- 🌐 Online
- 🏢 Offline
- 🔄 Hybrid
- 🤖 AI / ML
- 💻 Web
- 🔐 Cybersecurity

### ⏳ Deadline Tracking
- Displays registration deadlines
- Live countdown for upcoming deadlines
- Automatically identifies hackathons that are closing soon
- Shows registration status

### 🔗 Official Registration
Each hackathon can provide a link to its official Devpost page so users can view complete rules and register.

### 👨‍💻 Admin Dashboard
The admin can:
- Add hackathons
- Edit hackathons
- Delete hackathons
- View hackathon details
- Update hackathon information

### 🔄 Automatic Hackathon Discovery
HackHub can automatically retrieve hackathon information from a public hackathon feed.

The system:
1. Fetches available hackathon data
2. Filters unsuitable records
3. Detects duplicate hackathons
4. Adds new hackathons
5. Updates existing records
6. Stores the information in the database

### 🕐 Last Updated
The website displays the latest time the hackathon database was refreshed.

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Database
- SQLite
- Flask-SQLAlchemy

### Data Processing
- Python Requests
- Automatic data discovery and filtering

### Development Tools
- Visual Studio Code
- Git
- GitHub

---

## ⚙️ How HackHub Works

```text
                 Public Hackathon Feed
                         │
                         ▼
              Automatic Discovery System
                         │
                         ▼
                 Data Validation
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       New Hackathon           Existing Hackathon
             │                       │
             ▼                       ▼
           Add                    Update
             │                       │
             └───────────┬───────────┘
                         ▼
                   SQLite Database
                         │
                         ▼
                    Flask Backend
                         │
                         ▼
                  HackHub Website
                         │
                         ▼
                    Students
                    📂 Project Structure
Hackhub/
│
├── models/
│   ├── __init__.py
│   └── hackathon.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── templates/
│   ├── index.html
│   ├── hackathon.html
│   ├── admin.html
│   ├── add_hackathon.html
│   └── edit_hackathon.html
│
├── app.py
├── add_data.py
├── updater.py
├── discover_hackathons.py
├── import_discovered_hackathons.py
├── migrate_db.py
├── requirements.txt
└── .gitignore

💻 How to Run Locally
1. Clone the repository
git clone https://github.com/dhruthipjain/hackhub.git

2. Open the project
cd hackhub

3. Install dependencies
pip install -r requirements.txt

4. Run the Flask application
python app.py

5. Open the website
Open your browser and visit:
http://127.0.0.1:5000

👨‍💻 Admin Dashboard
The admin dashboard is available at:
http://127.0.0.1:5000/admin

From the dashboard, the administrator can manage hackathons and trigger an update of the hackathon database.

🔄 Automatic Data Updating
HackHub uses an automatic discovery script to retrieve hackathon information.
The main discovery process is handled by:
import_discovered_hackathons.py
The system checks the incoming data and prevents duplicate records based on hackathon information such as the official source URL and name.

📊 Current Project
HackHub has been tested with a database containing multiple hackathon records and successfully supports automatic discovery, updating, filtering, and deadline tracking.

🎯 Project Goal
The goal of HackHub is to make hackathon discovery easier for students by bringing relevant opportunities into a single, simple platform.

🚀 Future Improvements
Possible future improvements include:
- User accounts
- Bookmarking hackathons
- Email deadline reminders
- More advanced filtering
- Personalized hackathon recommendations
- Deployment as a public web application

👩‍💻 Author
Dhruthi P Jain
Computer Science Engineering Student

⭐ If you find this project useful, consider giving the repository a star!