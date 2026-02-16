import sqlite3
import os

def cleanup():
    db_path = 'trading_assistant.db'
    if not os.path.exists(db_path):
        print(f"No database found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Economic Events (Calendar)
        cursor.execute("DELETE FROM economic_events;")
        print("Cleared economic_events table.")

        # 2. Notifications (Often contains test alerts)
        # Check if table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications';")
        if cursor.fetchone():
            cursor.execute("DELETE FROM notifications;")
            print("Cleared notifications table.")

        # 3. Market Regime (Might have test data)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_regime';")
        if cursor.fetchone():
            cursor.execute("DELETE FROM market_regime;")
            print("Cleared market_regime table.")

        conn.commit()
        print("Database cleanup completed successfully.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
