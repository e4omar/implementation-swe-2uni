from server.Facade import ScheduleFacade

facade = ScheduleFacade()

def staff_menu(user):
    while True:
        print(f"\nWelcome, {user['name']} (Staff)")
        print("1. View Schedule")
        print("2. Submit Time-Off Request")
        print("3. Submit Shift-Change Request")
        print("0. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            schedule = facade.db.fetch_schedule_by_staff(user['staff_id'])
            if schedule:
                print("\nYour Schedule:")
                for entry in schedule:
                    print(entry)
            else:
                print("No schedule assigned.")

        elif choice == "2":
            request_id = input("Request ID: ")
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            reason = input("Reason: ")
            print(facade.submit_time_off(request_id, user['staff_id'], start, end, reason))

        elif choice == "3":
            request_id = input("Request ID: ")
            shift_id = input("Shift ID: ")
            start = input("New Start Time (HH:MM): ")
            end = input("New End Time (HH:MM): ")
            reason = input("Reason for change: ")
            print(facade.submit_shift_change(request_id, shift_id, user['staff_id'], start, end, reason))

        elif choice == "0":
            break
        else:
            print("Invalid option. Try again.")


def manager_menu(user):
    while True:
        print(f"\nWelcome, {user['name']} (Manager)")
        print("1. Create Schedule for Staff")
        print("2. View Time-Off Requests")
        print("3. View Shift-Change Requests")
        print("0. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            staff_id = input("Staff ID: ")
            date = input("Date (YYYY-MM-DD): ")
            start = input("Start Time: ")
            end = input("End Time: ")
            print(facade.create_staff_schedule(staff_id, date, start, end))

        elif choice == "2":
            requests = facade.db.get_all_time_off_requests()
            if requests:
                print("\n--- Time-Off Requests ---")
                for r in requests:
                    print(f"{r.request_id} | Staff: {r.staff_id} | {r.start_date} to {r.end_date} | Reason: {r.reason}")
            else:
                print("No time-off requests submitted.")

        elif choice == "3":
            requests = facade.db.get_all_shift_change_requests()
            if requests:
                print("\n--- Shift-Change Requests ---")
                for r in requests:
                    print(f"{r.request_id} | Staff: {r.staff_id} | Shift: {r.shift_id} | Time: {r.start_time}–{r.end_time} | Reason: {r.reason}")
            else:
                print("No shift-change requests submitted.")
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

# === Login Loop ===
if __name__ == "__main__":
    print("🔐 Log In to Scheduling System")

    while True:
        username = input("\nUsername (or type 'exit' to quit): ").strip()
        if username.lower() == "exit":
            print("Goodbye!")
            break

        password = input("Password: ").strip()
        user = facade.login(username, password)

        if user:
            if user["role"] == "staff":
                staff_menu(user)
            elif user["role"] == "manager":
                manager_menu(user)
        else:
            print("❌ Invalid login. Please try again.")

