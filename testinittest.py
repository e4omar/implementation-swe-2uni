import sqlite3
from datetime import datetime

DB_NAME = "reservations.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LoginCredential (
        login_credentials_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        login_credentials_id INTEGER,
        FOREIGN KEY (login_credentials_id) REFERENCES LoginCredential(login_credentials_id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Slot (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        availability_status TEXT DEFAULT 'Available'
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        slot_id INTEGER NOT NULL,
        date_time TEXT NOT NULL,
        table_number INTEGER,
        status TEXT DEFAULT 'Booked',
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Notification (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reservation_id INTEGER,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id)
    );
    ''')

    conn.commit()
    conn.close()
    print("✅ Reservation system database initialized correctly.")

# -------------------------------
# CUSTOMER FUNCTIONS
# -------------------------------

def view_available_slots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_id, start_time, end_time FROM Slot WHERE availability_status = 'Available'")
    slots = cursor.fetchall()
    conn.close()
    return slots

def book_slot(user_id, slot_id, table_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT availability_status FROM Slot WHERE slot_id = ?", (slot_id,))
    result = cursor.fetchone()
    if result is None or result[0] != "Available":
        conn.close()
        return "❌ Slot not available."

    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO Reservation (user_id, slot_id, date_time, table_number, status)
        VALUES (?, ?, ?, ?, 'Booked')
    ''', (user_id, slot_id, now, table_number))

    cursor.execute("UPDATE Slot SET availability_status = 'Booked' WHERE slot_id = ?", (slot_id,))

    message = "Your reservation is confirmed."
    cursor.execute('''
        INSERT INTO Notification (user_id, reservation_id, message, status)
        VALUES (?, last_insert_rowid(), ?, 'Pending')
    ''', (user_id, message))

    conn.commit()
    conn.close()
    return "✅ Reservation confirmed."

# -------------------------------
# STAFF FUNCTIONS
# -------------------------------

def view_all_reservations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Reservation.reservation_id, User.name, Slot.start_time, Slot.end_time, Reservation.status
        FROM Reservation
        JOIN User ON Reservation.user_id = User.user_id
        JOIN Slot ON Reservation.slot_id = Slot.slot_id
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def modify_reservation(reservation_id, new_slot_id, new_table_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT availability_status FROM Slot WHERE slot_id = ?", (new_slot_id,))
    slot = cursor.fetchone()
    if slot is None or slot[0] != "Available":
        conn.close()
        return "❌ New slot not available."

    cursor.execute('''
        UPDATE Reservation
        SET slot_id = ?, table_number = ?, status = 'Modified'
        WHERE reservation_id = ?
    ''', (new_slot_id, new_table_number, reservation_id))

    cursor.execute("UPDATE Slot SET availability_status = 'Booked' WHERE slot_id = ?", (new_slot_id,))

    conn.commit()
    conn.close()
    return "✅ Reservation updated."

def edit_slot(slot_id, new_start, new_end, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Slot
        SET start_time = ?, end_time = ?, availability_status = ?
        WHERE slot_id = ?
    ''', (new_start, new_end, new_status, slot_id))
    conn.commit()
    conn.close()
    return "✅ Slot updated."

# -------------------------------
# MAIN MENU
# -------------------------------

def main():
    initialize_database()
    while True:
        print("\n📋 Reservation System Menu")
        print("1. View available slots")
        print("2. Book a slot")
        print("3. View all reservations (staff)")
        print("4. Modify a reservation (staff)")
        print("5. Edit a slot (staff)")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            slots = view_available_slots()
            for s in slots:
                print(f"Slot ID: {s[0]}, Start: {s[1]}, End: {s[2]}")

        elif choice == "2":
            uid = int(input("Enter your user ID: "))
            sid = int(input("Enter slot ID to book: "))
            table = int(input("Enter table number: "))
            print(book_slot(uid, sid, table))

        elif choice == "3":
            reservations = view_all_reservations()
            for r in reservations:
                print(f"Reservation ID: {r[0]}, Name: {r[1]}, Start: {r[2]}, End: {r[3]}, Status: {r[4]}")

        elif choice == "4":
            rid = int(input("Enter reservation ID: "))
            new_sid = int(input("Enter new slot ID: "))
            new_table = int(input("Enter new table number: "))
            print(modify_reservation(rid, new_sid, new_table))

        elif choice == "5":
            sid = int(input("Enter slot ID to edit: "))
            start = input("Enter new start time (YYYY-MM-DD HH:MM): ")
            end = input("Enter new end time (YYYY-MM-DD HH:MM): ")
            status = input("Enter new availability status: ")
            print(edit_slot(sid, start, end, status))

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

