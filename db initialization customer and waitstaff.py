import sqlite3
from datetime import datetime

DB_NAME = "reservations.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------

conn = get_connection()
cursor = conn.cursor()

# Create LoginCredential table
cursor.execute('''
CREATE TABLE IF NOT EXISTS LoginCredential (
    login_credentials_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL  -- 'customer', 'staff', 'admin', etc.
);
''')

# Create User table (for both customers and staff)
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    login_credentials_id INTEGER,
    FOREIGN KEY (login_credentials_id) REFERENCES LoginCredential(login_credentials_id)
);
''')

# Create Slot table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Slot (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    availability_status TEXT DEFAULT 'Available'  -- 'Available', 'Booked', etc.
);
''')

# Create Reservation table
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

# Create Notification table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Notification (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reservation_id INTEGER,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',  -- 'Pending', 'Delivered', etc.
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
