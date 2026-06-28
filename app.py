"""
Portfolio Website — Flask Backend
Connects to MongoDB for dynamic content management.
Falls back to seed data if MongoDB is unavailable.
"""

import os
import re
import html
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Secure CORS configuration (origins can be restricted in production via environment variables)
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# ── MongoDB Connection ──────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/portfolio")
db = None

try:
    from pymongo import MongoClient
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    client.server_info()  # Force connection check
    db = client.get_database()
    print("[OK] Connected to MongoDB")
except Exception as e:
    print(f"[WARN] MongoDB not available ({e}). Using fallback data.")
    db = None


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
    """Fetch data from MongoDB or use fallback."""
    if db is not None:
        try:
            data = list(db[collection_name].find({}, {"_id": 0}))
            if data:
                return data if isinstance(fallback, list) else data[0]
        except Exception:
            pass
    return fallback


def seed_database():
    """Seed MongoDB with fallback data if collections are empty."""
    if db is None:
        return

    collections = {
        "profile": FALLBACK_PROFILE,
        "skills": FALLBACK_SKILLS,
        "education": FALLBACK_EDUCATION,
        "projects": FALLBACK_PROJECTS,
        "social_links": FALLBACK_SOCIAL,
    }

    for name, data in collections.items():
        if db[name].count_documents({}) == 0:
            if isinstance(data, list):
                db[name].insert_many(data)
            else:
                db[name].insert_one(data)
            print(f"  [SEED] Seeded '{name}' collection")


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

    if db is not None:
        try:
            db.contacts.insert_one(contact)
        except Exception as e:
            print(f"Failed to save contact: {e}")

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
