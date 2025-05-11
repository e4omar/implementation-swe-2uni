import sqlite3

DB_PATH = "scheduling.db"

def seed_staff_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sample staff and manager users
    users = [
        ("Alice", "staff", "alice", "pass123"),
        ("Bob", "manager", "bob", "admin456")
    ]

    for name, role, username, password in users:
        # Avoid inserting duplicates
        cursor.execute("SELECT * FROM Staff WHERE username = ?", (username,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO Staff (name, role, username, password)
                VALUES (?, ?, ?, ?)
            ''', (name, role, username, password))
            print(f"✅ Added user: {name} ({role})")
        else:
            print(f"ℹ️ User '{username}' already exists.")

    conn.commit()
    conn.close()
    print("🚀 Seeding complete.")

if __name__ == "__main__":
    seed_staff_users()
