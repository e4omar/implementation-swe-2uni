from server.Facade import ScheduleFacade

facade = ScheduleFacade()

def staff_menu(user):
    print(f"\nWelcome, {user['name']} (Staff)")
    print("1. View Schedule")
    print("2. Submit Time-Off Request")
    choice = input("Choose an option: ")

    if choice == "1":
        schedule = facade.db.fetch_schedule_by_staff(user['staff_id'])
        for entry in schedule:
            print(entry)
    elif choice == "2":
        request_id = input("Staff ID: ")
        start = input("Start Date (YYYY-MM-DD): ")
        end = input("End Date (YYYY-MM-DD): ")
        reason = input("Reason: ")
        print(facade.submit_time_off(request_id, user['staff_id'], start, end, reason))


def manager_menu(user):
    print(f"\nWelcome, {user['name']} (Manager)")
    print("1. Create Schedule for Staff")
    choice = input("Choose an option: ")

    if choice == "1":
        staff_id = input("Staff ID: ")
        date = input("Date (YYYY-MM-DD): ")
        start = input("Start Time: ")
        end = input("End Time: ")
        print(facade.create_staff_schedule(staff_id, date, start, end))


if __name__ == "__main__":
    print("🔐 Log In to Scheduling System")
    username = input("Username: ")
    password = input("Password: ")

    user = facade.login(username, password)

    if user:
        if user["role"] == "staff":
            staff_menu(user)
        elif user["role"] == "manager":
            manager_menu(user)
        else:
            print("Unknown role.")
    else:
        print("❌ Invalid login. Try again.")
