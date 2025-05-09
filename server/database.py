import sqlite3

DB_NAME = "scheduling.db"

# ─────────────────────────────────────────────
# Utility function to get a DB connection
# ─────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_NAME)


# ─────────────── STAFF ───────────────
def get_staff_by_credentials(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Staff WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result


# ─────────────── SCHEDULE ───────────────
def insert_schedule(staff_id, date, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO StaffSchedule (staff_id, shift_date, start_time, end_time)
        VALUES (?, ?, ?, ?)
    ''', (staff_id, date, start_time, end_time))
    conn.commit()
    conn.close()


def get_schedule_for_staff(staff_id):
    conn = sqlite3.connect("scheduling.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT schedule_id, shift_date, start_time, end_time
        FROM StaffSchedule
        WHERE staff_id = ?
        ORDER BY shift_date
    ''', (staff_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows



# ─────────────── TIME OFF ───────────────
def insert_time_off_request(staff_id, start_date, end_date, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO TimeOffRequest (staff_id, start_date, end_date, reason)
        VALUES (?, ?, ?, ?)
    ''', (staff_id, start_date, end_date, reason))
    conn.commit()
    conn.close()


def get_all_time_off_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TimeOffRequest ORDER BY start_date")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_time_off_status(request_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE TimeOffRequest
        SET status = ?
        WHERE request_id = ?
    ''', (new_status, request_id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0


# ─────────────── NOTIFICATIONS ───────────────
def add_notification(staff_id, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Notification (staff_id, message)
        VALUES (?, ?)
    ''', (staff_id, message))
    conn.commit()
    conn.close()


def get_notifications_for_staff(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT message FROM Notification
        WHERE staff_id = ? AND is_read = 0
    ''', (staff_id,))
    messages = cursor.fetchall()
    
    # Mark them as read
    cursor.execute('''
        UPDATE Notification
        SET is_read = 1
        WHERE staff_id = ?
    ''', (staff_id,))
    
    conn.commit()
    conn.close()
    return [msg[0] for msg in messages]

# ─────────────── Shift change Request ───────────────

def insert_shift_change_request(staff_id, shift_id, new_start, new_end, reason):
    conn = sqlite3.connect("scheduling.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ShiftChangeRequest (staff_id, shift_id, new_start_time, new_end_time, reason)
        VALUES (?, ?, ?, ?, ?)
    ''', (staff_id, shift_id, new_start, new_end, reason))
    conn.commit()
    conn.close()


def get_all_shift_change_requests():
    conn = sqlite3.connect("scheduling.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ShiftChangeRequest ORDER BY request_id")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_shift_change_status(request_id, new_status):
    conn = sqlite3.connect("scheduling.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE ShiftChangeRequest
        SET status = ?
        WHERE request_id = ?
    ''', (new_status, request_id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated > 0


