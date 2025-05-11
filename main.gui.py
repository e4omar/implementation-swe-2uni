import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import sqlite3

from backend.reservation_facade import (
    book_slot_for_customer,
    view_all_reservations,
    modify_existing_reservation,
    edit_existing_slot,
    list_available_slots
)

DB_NAME = "reservations.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS LoginCredential (
        login_credentials_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        login_credentials_id INTEGER,
        FOREIGN KEY (login_credentials_id) REFERENCES LoginCredential(login_credentials_id));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Slot (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        availability_status TEXT DEFAULT 'Available');''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Reservation (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        slot_id INTEGER NOT NULL,
        date_time TEXT NOT NULL,
        table_number INTEGER,
        status TEXT DEFAULT 'Booked',
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (slot_id) REFERENCES Slot(slot_id));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Notification (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reservation_id INTEGER,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id));''')

    conn.commit()
    conn.close()

def seed_test_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Notification")
    cursor.execute("DELETE FROM Reservation")
    cursor.execute("DELETE FROM Slot")
    cursor.execute("DELETE FROM User")
    cursor.execute("DELETE FROM LoginCredential")

    cursor.execute("""INSERT INTO LoginCredential (username, password_hash, role)
        VALUES ('cust1', 'hashed_pass', 'customer'),
               ('staff1', 'hashed_pass', 'staff')""")

    cursor.execute("""INSERT INTO User (name, email, login_credentials_id)
        VALUES ('Alice Customer', 'alice@example.com', 1),
               ('Bob Staff', 'bob@example.com', 2)""")

    now = datetime.now()
    for i in range(3):
        start = now.replace(hour=12 + i, minute=0).isoformat()
        end = now.replace(hour=13 + i, minute=0).isoformat()
        cursor.execute("INSERT INTO Slot (start_time, end_time, availability_status) VALUES (?, ?, 'Available')", (start, end))

    conn.commit()
    conn.close()
    print("✅ Test data seeded successfully.")

def show_customer_dashboard(user_id):
    dash = tk.Toplevel()
    dash.title("Customer Dashboard")

    def view_slots():
        slots = list_available_slots()
        msg = "\n".join([f"ID {s[0]}: {s[1]} to {s[2]}" for s in slots]) if slots else "No available slots."
        messagebox.showinfo("Available Slots", msg)

    def book():
        slot_id = simpledialog.askinteger("Book Slot", "Enter Slot ID:")
        table_number = simpledialog.askinteger("Book Slot", "Enter Table Number:")
        result = book_slot_for_customer(user_id, slot_id, table_number)
        messagebox.showinfo("Booking Result", result)

    tk.Button(dash, text="View Available Slots", command=view_slots).pack(pady=5)
    tk.Button(dash, text="Book a Slot", command=book).pack(pady=5)

def show_staff_dashboard():
    dash = tk.Toplevel()
    dash.title("Staff Dashboard")

    def view_reservations():
        data = view_all_reservations()
        msg = "\n".join([f"ID {r[0]}, {r[1]}: {r[2]} to {r[3]} [{r[4]}]" for r in data]) if data else "No reservations found."
        messagebox.showinfo("Reservations", msg)

    def modify():
        res_id = simpledialog.askinteger("Modify", "Reservation ID:")
        new_sid = simpledialog.askinteger("Modify", "New Slot ID:")
        new_table = simpledialog.askinteger("Modify", "New Table No:")
        result = modify_existing_reservation(res_id, new_sid, new_table)
        messagebox.showinfo("Modify Result", result)

    def edit():
        sid = simpledialog.askinteger("Edit Slot", "Slot ID:")
        start = simpledialog.askstring("Edit Slot", "New Start (YYYY-MM-DD HH:MM):")
        end = simpledialog.askstring("Edit Slot", "New End (YYYY-MM-DD HH:MM):")
        status = simpledialog.askstring("Edit Slot", "New Status:")
        result = edit_existing_slot(sid, start, end, status)
        messagebox.showinfo("Edit Result", result)

    tk.Button(dash, text="View Reservations", command=view_reservations).pack(pady=5)
    tk.Button(dash, text="Modify Reservation", command=modify).pack(pady=5)
    tk.Button(dash, text="Edit Slot", command=edit).pack(pady=5)

def login_window():
    def try_login():
        username = username_entry.get()
        role = role_entry.get().lower()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT login_credentials_id, role FROM LoginCredential WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and user[1] == role:
            if role == "customer":
                cursor.execute("SELECT user_id FROM User WHERE login_credentials_id = ?", (user[0],))
                uid = cursor.fetchone()
                if uid:
                    login.destroy()
                    show_customer_dashboard(uid[0])
            elif role == "staff":
                login.destroy()
                show_staff_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or role.")
        conn.close()

    login = tk.Tk()
    login.title("Login")
    tk.Label(login, text="Username:").pack()
    username_entry = tk.Entry(login)
    username_entry.pack()
    tk.Label(login, text="Role (customer/staff):").pack()
    role_entry = tk.Entry(login)
    role_entry.pack()
    tk.Button(login, text="Login", command=try_login).pack(pady=10)
    login.mainloop()

if __name__ == "__main__":
    initialize_database()
    seed_test_data()
    login_window()
