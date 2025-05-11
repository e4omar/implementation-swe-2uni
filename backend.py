

import sqlite3
DB_NAME = "reservations.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# (rest of code remains unchanged below...)

# ────────────── Functions Below ──────────────

def get_available_slots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_id, start_time, end_time FROM Slot WHERE availability_status = 'Available'")
    result = cursor.fetchall()
    conn.close()
    return result

def insert_reservation(user_id, slot_id, date_time, table_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Reservation (user_id, slot_id, date_time, table_number, status)
        VALUES (?, ?, ?, ?, 'Booked')
    ''', (user_id, slot_id, date_time, table_number))
    conn.commit()
    conn.close()

def update_slot_status(slot_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Slot SET availability_status = ? WHERE slot_id = ?", (new_status, slot_id))
    conn.commit()
    conn.close()

def log_notification(user_id, reservation_id, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Notification (user_id, reservation_id, message, status)
        VALUES (?, ?, ?, 'Pending')
    ''', (user_id, reservation_id, message))
    conn.commit()
    conn.close()

def get_all_reservations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Reservation.reservation_id, User.name, Slot.start_time, Slot.end_time, Reservation.status
        FROM Reservation
        JOIN User ON Reservation.user_id = User.user_id
        JOIN Slot ON Reservation.slot_id = Slot.slot_id
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def update_reservation(reservation_id, new_slot_id, new_table):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Reservation
        SET slot_id = ?, table_number = ?, status = 'Modified'
        WHERE reservation_id = ?
    ''', (new_slot_id, new_table, reservation_id))
    conn.commit()
    conn.close()

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


    # !!!!
#
# 1. need to create a folder called 'backend' in the same place as main_gui.py file.
# 2. then to create3 files
#    - database_access.py
#    - reservation_controller.py
#    - reservation_facade.py
# 3.  create an empty file named '__init__.py' inside the backend folder.

