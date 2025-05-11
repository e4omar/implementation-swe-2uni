import tkinter as tk
from tkinter import messagebox
from server.facade import Schedulefacade

facade = Schedulefacade()

# ─────────────── STAFF DASHBOARD ───────────────
def show_staff_dashboard(user):
    dashboard = tk.Toplevel()
    dashboard.title("Staff Dashboard")
    dashboard.geometry("350x200")
    tk.Label(dashboard, text=f"Welcome, {user['name']} (Staff)", font=("Arial", 14)).pack(pady=10)

    # Show notifications
    notes = facade.get_notifications(user["staff_id"])
    if notes:
        notif_text = "\n".join([f"- {msg}" for msg in notes])
        messagebox.showinfo("New Notifications", notif_text)


    def view_schedule():
        schedule = facade.view_schedule(user["staff_id"])
        result = "\n".join([f"{s[1]}: {s[2]} - {s[3]}" for s in schedule]) if schedule else "No schedule found."
        messagebox.showinfo("My Schedule", result)

    def submit_time_off():
        top = tk.Toplevel()
        top.title("Submit Time-Off Request")

        tk.Label(top, text="Start Date (YYYY-MM-DD):").pack()
        start = tk.Entry(top)
        start.pack()

        tk.Label(top, text="End Date (YYYY-MM-DD):").pack()
        end = tk.Entry(top)
        end.pack()

        tk.Label(top, text="Reason:").pack()
        reason = tk.Entry(top)
        reason.pack()

        def submit():
            msg = facade.submit_time_off(user["staff_id"], start.get(), end.get(), reason.get())
            messagebox.showinfo("Submitted", msg)
            top.destroy()

        tk.Button(top, text="Submit", command=submit).pack(pady=5)

    def submit_shift_change():
        top = tk.Toplevel()
        top.title("Submit Shift-Change Request")

        tk.Label(top, text="Shift ID:").pack()
        shift_id = tk.Entry(top)
        shift_id.pack()

        tk.Label(top, text="New Start Time (HH:MM):").pack()
        new_start = tk.Entry(top)
        new_start.pack()

        tk.Label(top, text="New End Time (HH:MM):").pack()
        new_end = tk.Entry(top)
        new_end.pack()

        tk.Label(top, text="Reason:").pack()
        reason = tk.Entry(top)
        reason.pack()

        def submit():
            msg = facade.submit_shift_change(user["staff_id"], shift_id.get(), new_start.get(), new_end.get(), reason.get())
            messagebox.showinfo("Submitted", msg)
            top.destroy()

        tk.Button(top, text="Submit", command=submit).pack(pady=5)


    tk.Button(dashboard, text="View Schedule", command=view_schedule).pack(pady=5)
    tk.Button(dashboard, text="Submit Time-Off Request", command=submit_time_off).pack(pady=5)
    tk.Button(dashboard, text="Submit Shift-Change Request", command=submit_shift_change).pack(pady=5)
    tk.Button(dashboard, text="Exit", command=dashboard.destroy).pack(pady=10)


# ─────────────── LOGIN WINDOW ───────────────
def login_window():
    def attempt_login():
        username = entry_username.get()
        password = entry_password.get()
        user = facade.login(username, password)
        if user:
            messagebox.showinfo("Login Successful", f"Welcome, {user['name']} ({user['role']})")
            login.destroy()
            if user["role"] == "staff":
                show_staff_dashboard(user)
            elif user["role"] == "manager":
                show_manager_dashboard(user)
            else:
                messagebox.showinfo("Role Unsupported", f"Unknown role: {user['role']}")

        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    login = tk.Toplevel()
    login.title("Scheduling System Login")
    login.geometry("300x200")

    tk.Label(login, text="Username:").pack(pady=5)
    entry_username = tk.Entry(login)
    entry_username.pack()

    tk.Label(login, text="Password:").pack(pady=5)
    entry_password = tk.Entry(login, show="*")
    entry_password.pack()

    tk.Button(login, text="Login", command=attempt_login).pack(pady=15)
    login.mainloop()

def show_manager_dashboard(user):
    dashboard = tk.Toplevel()
    dashboard.title("Manager Dashboard")
    dashboard.geometry("400x300")
    tk.Label(dashboard, text=f"Welcome, {user['name']} (Manager)", font=("Arial", 14)).pack(pady=10)


    def view_shift_requests():
            requests = facade.view_all_shift_change_requests()
            if not requests:
                messagebox.showinfo("Shift Changes", "No shift-change requests.")
                return
            result = "\n\n".join([
                f"ID: {r[0]} | Staff: {r[1]} | Shift: {r[2]}\nNew Time: {r[3]} → {r[4]}\nReason: {r[5]} | Status: {r[6]}"
                for r in requests
            ])
            messagebox.showinfo("Shift-Change Requests", result)

    def approve_shift_request():
        top = tk.Toplevel()
        top.title("Approve Shift-Change Request")

        tk.Label(top, text="Request ID:").pack()
        req_id = tk.Entry(top)
        req_id.pack()

        tk.Label(top, text="Staff ID:").pack()
        staff_id = tk.Entry(top)
        staff_id.pack()

        tk.Label(top, text="New Status (Approved/Rejected):").pack()
        status = tk.Entry(top)
        status.pack()

        def submit():
            msg = facade.update_shift_change_status(req_id.get(), status.get(), staff_id.get())
            messagebox.showinfo("Status Update", msg)
            top.destroy()

        tk.Button(top, text="Submit", command=submit).pack(pady=5)

    def view_requests():
        requests = facade.view_all_time_off_requests()
        if not requests:
            messagebox.showinfo("Requests", "No time-off requests.")
            return
        result = "\n\n".join([
            f"ID: {r[0]} | Staff: {r[1]}\n{r[2]} → {r[3]}\nReason: {r[4]} | Status: {r[5]}"
            for r in requests
        ])
        messagebox.showinfo("Time-Off Requests", result)

    def approve_request():
        top = tk.Toplevel()
        top.title("Approve Time-Off Request")

        tk.Label(top, text="Request ID:").pack()
        req_id = tk.Entry(top)
        req_id.pack()

        tk.Label(top, text="Staff ID:").pack()
        staff_id = tk.Entry(top)
        staff_id.pack()

        tk.Label(top, text="New Status (Approved/Rejected):").pack()
        status = tk.Entry(top)
        status.pack()

        def submit():
            msg = facade.update_time_off_status(req_id.get(), status.get(), staff_id.get())
            messagebox.showinfo("Status Update", msg)
            top.destroy()

        tk.Button(top, text="Submit", command=submit).pack(pady=5)

    def create_schedule():
        top = tk.Toplevel()
        top.title("Create Staff Schedule")

        tk.Label(top, text="Staff ID:").pack()
        staff_id = tk.Entry(top)
        staff_id.pack()

        tk.Label(top, text="Date (YYYY-MM-DD):").pack()
        date = tk.Entry(top)
        date.pack()

        tk.Label(top, text="Start Time (HH:MM):").pack()
        start = tk.Entry(top)
        start.pack()

        tk.Label(top, text="End Time (HH:MM):").pack()
        end = tk.Entry(top)
        end.pack()

        def submit():
            msg = facade.create_schedule(staff_id.get(), date.get(), start.get(), end.get())
            messagebox.showinfo("Schedule Created", msg)
            top.destroy()

        tk.Button(top, text="Submit", command=submit).pack(pady=5)

    def view_staff_records():
        records = facade.get_all_staff()
        if not records:
            messagebox.showinfo("Staff Records", "No staff found.")
            return
        result = "\n\n".join([f"ID: {r[0]} | Name: {r[1]} | Role: {r[2]} | Username: {r[3]}" for r in records])
        messagebox.showinfo("Staff Records", result)



    tk.Button(dashboard, text="View Time-Off Requests", command=view_requests).pack(pady=5)
    tk.Button(dashboard, text="Approve/Reject Time-Off", command=approve_request).pack(pady=5)
    tk.Button(dashboard, text="Create Staff Schedule", command=create_schedule).pack(pady=5)
    tk.Button(dashboard, text="View Shift-Change Requests", command=view_shift_requests).pack(pady=5)
    tk.Button(dashboard, text="Approve/Reject Shift Change", command=approve_shift_request).pack(pady=5)
    tk.Button(dashboard, text="View Staff Records", command=view_staff_records).pack(pady=5)
    tk.Button(dashboard, text="Exit", command=dashboard.destroy).pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the base root window
    login_window()
    root.mainloop()
