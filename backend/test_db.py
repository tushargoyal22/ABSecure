from backend.app.config.database import get_database

try:
    db = get_database()
    print("✅ Database connection successful:", db.list_collection_names())
except Exception as e:
    print("❌ Database connection error:", e)
