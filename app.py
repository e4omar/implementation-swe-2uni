from server.Facade import ScheduleFacade

if __name__ == "__main__":
    facade = ScheduleFacade()
    print(facade.create_staff_schedule("S101", "2025-05-10", "09:00", "17:00"))
    print(facade.submit_time_off("R201", "S101", "2025-05-15", "2025-05-18", "Vacation"))
    print(facade.submit_shift_change("R202", "SHIFT1", "S101", "14:00", "22:00", "Doctor appointment"))

