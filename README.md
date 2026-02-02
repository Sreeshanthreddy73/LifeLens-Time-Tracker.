# LifeLens — Personal Productivity Time Tracker

LifeLens is a powerful, minimal self-tracking tool designed to help you master your time. By logging your daily activities, LifeLens provides insightful analytics to help you understand your productivity patterns.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.x
- pip (Python package manager)

### 2. Installation
Clone or download the project files, then navigate to the project directory and install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Running the App
Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:
`http://localhost:5000`

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Authentication:** Flask-Login, Werkzeug (Security)
- **Database:** SQLite, SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Jinja2
- **Charts:** Chart.js

## ✨ Features
- **Secure Authentication:** Register and log in. Each user has private data.
- **Activity Logging:** Add activities with custom start/end times and categories.
- **Productivity Scoring:** Automatically calculates efficiency based on productive vs. waste time.
- **Visual Analytics:** Real-time Pie and Bar charts for time distribution.
- **History Tracking:** Detailed view of past logs and daily summaries.
- **Responsive Design:** Works beautifully on desktop and mobile.

## 📁 Project Structure
- `app.py`: Main application logic and routes.
- `models.py`: Database models for Users and Activities.
- `templates/`: HTML templates using Jinja.
- `static/`: CSS and Client-side JavaScript.
- `requirements.txt`: Project dependencies.
