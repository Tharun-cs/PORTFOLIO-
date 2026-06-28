from pymongo import MongoClient

print("Connecting to local MongoDB on port 27017 (no auth)...")
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)

try:
    # 1. Create Admin User
    print("Creating admin user in 'admin' database...")
    admin_db = client.admin
    admin_db.command(
        "createUser",
        "admin",
        pwd="adminSecurePassword2026!",
        roles=[
            {"role": "userAdminAnyDatabase", "db": "admin"},
            {"role": "dbAdminAnyDatabase", "db": "admin"},
            {"role": "readWriteAnyDatabase", "db": "admin"}
        ]
    )
    print("[SUCCESS] Admin user created.")
except Exception as e:
    print(f"[INFO] Admin user may already exist or error occurred: {e}")

try:
    # 2. Create Application User
    print("Creating application user in 'portfolio' database...")
    portfolio_db = client.portfolio
    portfolio_db.command(
        "createUser",
        "portfolio_user",
        pwd="portfolioSecurePassword2026!",
        roles=[
            {"role": "readWrite", "db": "portfolio"}
        ]
    )
    print("[SUCCESS] Portfolio user created.")
except Exception as e:
    print(f"[INFO] Portfolio user may already exist or error occurred: {e}")

print("User creation complete.")
