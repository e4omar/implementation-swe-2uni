import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect("scheduling.db")
cursor = conn.cursor()

# Create Staff table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'staff' or 'manager'
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

# Create Staff Schedule table
cursor.execute('''
CREATE TABLE IF NOT EXISTS StaffSchedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);
''')

# Create Time Off Requests table
cursor.execute('''
CREATE TABLE IF NOT EXISTS TimeOffRequest (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);
''')

# Create Shift Change Requests table
cursor.execute('''
CREATE TABLE IF NOT EXISTS ShiftChangeRequest (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    shift_id INTEGER NOT NULL,
    new_start_time TEXT NOT NULL,
    new_end_time TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (shift_id) REFERENCES StaffSchedule(schedule_id)
);
''')

# Create Notifications table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Notification (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);
''')

# Commit and close
conn.commit()
conn.close()

print("✅ Database initialized successfully.")
    
