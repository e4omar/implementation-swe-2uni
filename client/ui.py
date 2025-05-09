import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from server.facade import ScheduleFacade

facade = ScheduleFacade()

def staff_menu(user):
    staff_id = user["staff_id"]
    print(f"\n🔔 Welcome, {user['name']} (Staff)")

    # Show notifications
    notifications = facade.get_notifications(staff_id)
    if notifications:
        print("\n📨 You have new notifications:")
        for note in notifications:
            print(f"- {note}")
    else:
        print("\n✅ No new notifications.")

    while True:
        print("\n📋 Staff Menu:")
        print("1. View My Schedule")
        print("2. Submit Time-Off Request")
        print("0. Logout")

        choice = input("Select an option: ")

        if choice == "1":
            schedule = facade.view_schedule(staff_id)
            if isinstance(schedule, str):
                print(schedule)
            else:
                print("\n📅 Your Schedule:")
                for shift_id, date, start, end in schedule:
                     print(f"ID {shift_id} | {date}: {start} to {end}")

        elif choice == "2":
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            reason = input("Reason: ")
            print(facade.submit_time_off(staff_id, start, end, reason))

        elif choice == "3":
            shift_id = input("Shift ID: ")
            new_start = input("New Start Time (HH:MM): ")
            new_end = input("New End Time (HH:MM): ")
            reason = input("Reason: ")
            print(facade.submit_shift_change(staff_id, shift_id, new_start, new_end, reason))

        elif choice == "0":
            break
        else:
            print("❌ Invalid option. Try again.")


def manager_menu(user):
    print(f"\n🔐 Welcome, {user['name']} (Manager)")

    while True:
        print("\n📋 Manager Menu:")
        print("1. Create Staff Schedule")
        print("2. View Time-Off Requests")
        print("3. Approve/Reject Time-Off Request")
        print("0. Logout")

        choice = input("Select an option: ")

        if choice == "1":
            staff_id = input("Enter Staff ID: ")
            date = input("Date (YYYY-MM-DD): ")
            start = input("Start Time (HH:MM): ")
            end = input("End Time (HH:MM): ")
            print(facade.create_schedule(staff_id, date, start, end))

        elif choice == "2":
            requests = facade.view_all_time_off_requests()
            print("\n📄 Time-Off Requests:")
            for req in requests:
                print(f"ID {req[0]} | Staff {req[1]} | {req[2]} to {req[3]} | Reason: {req[4]} | Status: {req[5]}")

        elif choice == "3":
            request_id = input("Request ID: ")
            staff_id = input("Staff ID: ")  # Used for notification
            status = input("New Status (Approved/Rejected): ")
            print(facade.update_time_off_status(request_id, status, staff_id))

        elif choice == "4":
            requests = facade.view_all_shift_change_requests()
            print("\n📄 Shift-Change Requests:")
            for req in requests:
                print(f"ID {req[0]} | Staff {req[1]} | Shift {req[2]} | {req[3]} → {req[4]} | Reason: {req[5]} | Status: {req[6]}")

        elif choice == "5":
            request_id = input("Request ID: ")
            staff_id = input("Staff ID: ")
            status = input("New Status (Approved/Rejected): ")
            print(facade.update_shift_change_status(request_id, status, staff_id))

        elif choice == "0":
            break
        else:
            print("❌ Invalid option. Try again.")


# ─────────── App Entry Point ───────────
def run():
    while True:
        print("\n🔐 Log In to Scheduling System")
        username = input("Username (or type 'exit' to quit): ")
        if username.lower() == "exit":
            print("Goodbye!")
            break

        password = input("Password: ")
        user = facade.login(username, password)

        if user:
            if user["role"] == "staff":
                staff_menu(user)
            elif user["role"] == "manager":
                manager_menu(user)
            else:
                print("⚠️ Unknown role.")
        else:
            print("❌ Invalid credentials.")

# Allow running directly
if __name__ == "__main__":
    run()
