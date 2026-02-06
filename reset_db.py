"""
Database reset script for LifeLens
This will drop all tables and recreate them with the new schema
WARNING: This will delete all existing data!
"""
from app import app, db

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables with new schema...")
    db.create_all()
    print("✅ Database reset successfully!")
    print("New tables created:")
    print("  - User (with last_activity_date column)")
    print("  - Activity")
    print("  - DiaryEntry (NEW!)")
    print("\nYou can now run the app with: python app.py")
