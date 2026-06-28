"""
Portfolio Website — Flask Backend
Connects to PostgreSQL for dynamic content management.
Falls back to seed data if PostgreSQL is unavailable.
"""

import os
import re
import html
import json
try:
    import psycopg2
    from psycopg2.extras import Json
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Secure CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# ── PostgreSQL Connection ───────────────────────────────────────────
# Use POSTGRES_URL which is automatically provided by Vercel Postgres
DATABASE_URL = os.getenv("POSTGRES_URL")

def get_db_connection():
    if not DATABASE_URL or not HAS_POSTGRES:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"[WARN] Postgres not available ({e}). Using fallback data.")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            # Table for JSONB collections
            cur.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_data (
                    collection_name VARCHAR(50) PRIMARY KEY,
                    data JSONB
                );
            """)
            # Table for contact messages
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    subject VARCHAR(255),
                    message TEXT,
                    timestamp TIMESTAMP
                );
            """)
    except Exception as e:
        print(f"[ERROR] Failed to init DB: {e}")
    finally:
        conn.close()

# Initialize DB on startup
init_db()

# ── Fallback Data ───────────────────────────────────────────────────
FALLBACK_PROFILE = {
    "name": "Tharun D",
    "greeting": "Hi There,",
    "roles": ["Frontend Developer", "Computer Science Student", "UI/UX Designer", "Wordpress Developer"],
    "bio": "Motivated and detail-oriented Computer Science Engineering student with knowledge in HTML, CSS, and UI/UX design. Passionate about creating responsive and user-friendly web applications with clean and modern interfaces. Quick learner with strong problem-solving and teamwork skills, seeking an internship opportunity to gain practical experience and contribute effectively to innovative projects.",
    "bio_short": "A motivated Computer Science Engineering student passionate about frontend web development and UI/UX design.",
    "experience_years": "Student",
    "projects_completed": "5+",
    "happy_clients": "Fresher",
    "email": "tharund448@gmail.com",
    "phone": "+91 63740 52069",
    "location": "Karur, Tamilnadu",
}

FALLBACK_SKILLS = [
    {"name": "HTML",                    "percentage": 95, "category": "Frontend"},
    {"name": "CSS",                     "percentage": 90, "category": "Frontend"},
    {"name": "UI/UX Design",            "percentage": 85, "category": "Frontend"},
    {"name": "Responsive Web Design",   "percentage": 90, "category": "Frontend"},
    {"name": "Basic Web Page Designing","percentage": 85, "category": "Frontend"},
    {"name": "WordPress",               "percentage": 80, "category": "Frontend"},
    {"name": "Python",                  "percentage": 85, "category": "Programming"},
    {"name": "Java",                    "percentage": 80, "category": "Programming"},
    {"name": "C Programming",           "percentage": 85, "category": "Programming"},
    {"name": "C++",                     "percentage": 80, "category": "Programming"},
    {"name": "Problem Solving",         "percentage": 90, "category": "Strengths"},
    {"name": "Team Collaboration",      "percentage": 95, "category": "Strengths"},
    {"name": "Time Management",         "percentage": 85, "category": "Strengths"},
    {"name": "Adaptability",            "percentage": 90, "category": "Strengths"},
]

FALLBACK_EDUCATION = [
    {
        "degree": "Bachelor of Engineering (B.E.) – Computer Science and Engineering",
        "institution": "Sree Sakthi Engineering College",
        "year": "2024 – 2028",
        "description": "Currently pursuing B.E. in Computer Science and Engineering. Maintaining a strong academic record with a CGPA of 8.3.",
    },
    {
        "degree": "Higher Secondary (Class XII)",
        "institution": "R.N. Matric. Hr. Sec. School",
        "year": "2023",
        "description": "Completed Higher Secondary education with a percentage of 70%.",
    },
    {
        "degree": "Secondary School (Class X)",
        "institution": "R.N. Matric. Hr. Sec. School",
        "year": "2021",
        "description": "Completed Secondary School education with a percentage of 65%.",
    },
]

FALLBACK_PROJECTS = [
    {
        "title": "Sentiment Analysis Web App",
        "description": "NLP-based web application that analyzes text sentiment (Positive/Negative/Neutral) using a trained Naive Bayes classifier on movie review datasets.",
        "tech_stack": ["Python", "NLTK", "Scikit-learn", "Flask", "HTML/CSS"],
        "category": "AI & ML",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Real-Time Face Detection",
        "description": "Real-time face and eye detection system using OpenCV's Haar Cascade Classifier. Supports webcam feed and image uploads.",
        "tech_stack": ["Python", "OpenCV", "Haar Cascade", "NumPy"],
        "category": "AI & ML",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Disease Prediction System",
        "description": "Machine learning model that predicts potential diseases based on symptom inputs using Decision Tree and Random Forest algorithms.",
        "tech_stack": ["Python", "Scikit-learn", "Pandas", "Flask"],
        "category": "AI & ML",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Spam Email Classifier",
        "description": "Email spam detection classifier built with TF-IDF vectorization and Logistic Regression achieving 97%+ accuracy on the SMS Spam Collection dataset.",
        "tech_stack": ["Python", "Scikit-learn", "TF-IDF", "Pandas"],
        "category": "AI & ML",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Responsive Personal Portfolio",
        "description": "A clean, animated personal website showcasing qualifications, skills, and contact forms built with Flask and MongoDB.",
        "tech_stack": ["HTML5", "CSS3", "JavaScript", "Flask", "MongoDB"],
        "category": "Frontend",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Dynamic Weather Dashboard",
        "description": "Weather forecasting application fetching real-time data using OpenWeather API with 7-day forecast and location search.",
        "tech_stack": ["HTML5", "CSS3", "JavaScript", "API Integration"],
        "category": "Frontend",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
    {
        "title": "Student Database System",
        "description": "A console-based C++ application for tracking student grades, records, and course registration using file handling and OOPs principles.",
        "tech_stack": ["C++", "File Handling", "OOPs"],
        "category": "Backend",
        "live_url": "#",
        "github_url": "https://github.com/Tharun-cs",
    },
]

FALLBACK_SOCIAL = [
    {"platform": "LinkedIn", "url": "https://www.linkedin.com/in/tharun-d-b84b56364/", "icon": "linkedin-in"},
    {"platform": "GitHub", "url": "https://github.com/Tharun-cs", "icon": "github"},
    {"platform": "Instagram", "url": "https://www.instagram.com/itz__ranger__", "icon": "instagram"},
    {"platform": "Twitter", "url": "https://x.com/Tharunduri", "icon": "x-twitter"},
]


# ── Helper Functions & Security Helpers ──────────────────────────────
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def sanitize_html(text):
    """Sanitize input string by escaping HTML special characters."""
    if not isinstance(text, str):
        return ""
    return html.escape(text.strip())

def get_data(collection_name, fallback):
    """Fetch data from Postgres JSONB or use fallback."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT data FROM portfolio_data WHERE collection_name = %s;", (collection_name,))
                result = cur.fetchone()
                if result and result[0]:
                    return result[0]
        except Exception:
            pass
        finally:
            conn.close()
    return fallback


def seed_database():
    """Seed Postgres with fallback data if tables are empty."""
    conn = get_db_connection()
    if not conn:
        return

    collections = {
        "profile": FALLBACK_PROFILE,
        "skills": FALLBACK_SKILLS,
        "education": FALLBACK_EDUCATION,
        "projects": FALLBACK_PROJECTS,
        "social_links": FALLBACK_SOCIAL,
    }

    try:
        with conn.cursor() as cur:
            for name, data in collections.items():
                cur.execute("SELECT 1 FROM portfolio_data WHERE collection_name = %s;", (name,))
                if not cur.fetchone():
                    # Insert data as JSONB
                    cur.execute(
                        "INSERT INTO portfolio_data (collection_name, data) VALUES (%s, %s);",
                        (name, Json(data))
                    )
                    print(f"  [SEED] Seeded '{name}' collection to Postgres")
    except Exception as e:
        print(f"[ERROR] Seeding failed: {e}")
    finally:
        conn.close()

# Automatically seed when app loads
seed_database()

# ── Routes ──────────────────────────────────────────────────────────
@app.route("/")
def home():
    """Render the main portfolio page."""
    profile = get_data("profile", FALLBACK_PROFILE)
    skills = get_data("skills", FALLBACK_SKILLS)
    education = get_data("education", FALLBACK_EDUCATION)
    projects = get_data("projects", FALLBACK_PROJECTS)
    social_links = get_data("social_links", FALLBACK_SOCIAL)

    # Group skills by category
    skills_grouped = {}
    for skill in skills:
        cat = skill.get("category", "Other")
        skills_grouped.setdefault(cat, []).append(skill)

    return render_template(
        "index.html",
        profile=profile,
        skills=skills,
        skills_grouped=skills_grouped,
        education=education,
        projects=projects,
        social_links=social_links,
    )


@app.route("/api/contact", methods=["POST"])
def submit_contact():
    """Handle contact form submissions with sanitization and validation."""
    data = request.get_json() or request.form.to_dict()

    name = sanitize_html(data.get("name", ""))
    email = data.get("email", "").strip()
    subject = sanitize_html(data.get("subject", ""))
    message = sanitize_html(data.get("message", ""))

    if not all([name, email, message]):
        return jsonify({"success": False, "error": "Name, email, and message are required."}), 400

    if not EMAIL_REGEX.match(email):
        return jsonify({"success": False, "error": "Invalid email address format."}), 400

    contact = {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO contacts (name, email, subject, message, timestamp) VALUES (%s, %s, %s, %s, %s);",
                    (name, email, subject, message, datetime.utcnow())
                )
        except Exception as e:
            print(f"Failed to save contact: {e}")
        finally:
            conn.close()

    return jsonify({"success": True, "message": "Thank you! Your message has been sent."})

@app.route("/api/projects", methods=["GET"])
def get_projects():
    """API endpoint to fetch projects."""
    projects = get_data("projects", FALLBACK_PROJECTS)
    return jsonify(projects)


# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed_database()
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=5000, debug=debug)
