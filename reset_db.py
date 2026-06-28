from app import db, FALLBACK_PROFILE, FALLBACK_SKILLS, FALLBACK_EDUCATION, FALLBACK_PROJECTS, FALLBACK_SOCIAL

if db is None:
    print("[ERROR] MongoDB database is not available. Check your credentials in .env.")
    exit(1)

# Clear collections
db.profile.delete_many({})
db.skills.delete_many({})
db.education.delete_many({})
db.projects.delete_many({})
db.social_links.delete_many({})

print("Cleared database collections.")

# Insert new data
db.profile.insert_one(FALLBACK_PROFILE)
db.skills.insert_many(FALLBACK_SKILLS)
db.education.insert_many(FALLBACK_EDUCATION)
db.projects.insert_many(FALLBACK_PROJECTS)
db.social_links.insert_many(FALLBACK_SOCIAL)

print("Database populated successfully with CV data.")
