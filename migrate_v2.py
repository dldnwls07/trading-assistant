import sqlite3
import os
from src.config import settings

def migrate_db():
    db_path = settings.DB_PATH
    print(f"Migrating database at {db_path}...")
    
    if not os.path.exists(db_path):
        print("Database file not found. It will be created when the app runs.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("ai_pre_analysis", "TEXT"),
        ("ai_post_analysis", "TEXT"),
        ("ai_image_url", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE economic_events ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to economic_events table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding column {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_db()
