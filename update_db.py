from app import db

if db is None:
    print("[ERROR] MongoDB database is not available. Check your credentials in .env.")
    exit(1)

# Update LinkedIn
r1 = db.social_links.update_one(
    {"platform": "LinkedIn"},
    {"$set": {"url": "https://www.linkedin.com/in/tharun-d-b84b56364/"}}
)
print(f"LinkedIn: updated {r1.modified_count}")

# Update GitHub
r2 = db.social_links.update_one(
    {"platform": "GitHub"},
    {"$set": {"url": "https://github.com/Tharun-cs"}}
)
print(f"GitHub: updated {r2.modified_count}")

# Update Instagram
r3 = db.social_links.update_one(
    {"platform": "Instagram"},
    {"$set": {"url": "https://www.instagram.com/itz__ranger__"}}
)
print(f"Instagram: updated {r3.modified_count}")

# Update Twitter
r4 = db.social_links.update_one(
    {"platform": "Twitter"},
    {"$set": {
        "url": "https://x.com/Tharunduri",
        "icon": "x-twitter"
    }}
)
print(f"Twitter/X: updated {r4.modified_count}")
