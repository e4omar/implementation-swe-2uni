import sqlite3

DB_PATH = "scheduling.db"

def seed_demo_shifts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if Alice exists and get her staff_id
    cursor.execute("SELECT staff_id FROM Staff WHERE username = 'alice'")
    result = cursor.fetchone()

    if not result:
        print(" Alice (staff) not found. Please seed users first.")
        return

    staff_id = result[0]

    # Demo shifts to insert
    demo_shifts = [
        (staff_id, "2025-06-10", "10:00", "16:00"),
        (staff_id, "2025-06-11", "09:00", "15:00"),
        (staff_id, "2025-06-12", "11:00", "17:00")
    ]

    for shift in demo_shifts:
        cursor.execute('''
            INSERT INTO StaffSchedule (staff_id, shift_date, start_time, end_time)
            VALUES (?, ?, ?, ?)
        ''', shift)

    conn.commit()
    conn.close()
    print(" Demo shifts seeded for Alice.")

if __name__ == "__main__":
    seed_demo_shifts()
