from server import database

class ScheduleController:
    def login(self, username, password):
        user = database.get_staff_by_credentials(username, password)
        if user:
            return {
                "staff_id": user[0],
                "name": user[1],
                "role": user[2]
            }
        return None

    def submit_time_off_request(self, staff_id, start_date, end_date, reason):
        if not start_date or not end_date or not reason:
            return "❌ Missing required information."
        database.insert_time_off_request(staff_id, start_date, end_date, reason)
        return "✅ Time-off request submitted."

    def get_all_time_off_requests(self):
        return database.get_all_time_off_requests()

    def update_time_off_status(self, request_id, status):
        success = database.update_time_off_status(request_id, status)
        return "✅ Status updated." if success else "❌ Request not found."

    def create_schedule(self, staff_id, date, start_time, end_time):
        if not date or not start_time or not end_time:
            return "❌ Missing schedule details."
        database.insert_schedule(staff_id, date, start_time, end_time)
        return f"✅ Schedule created for staff ID {staff_id} on {date}."

    def view_schedule(self, staff_id):
        schedule = database.get_schedule_for_staff(staff_id)
        if schedule:
            return schedule
        return "No schedule found."

    def get_notifications(self, staff_id):
        return database.get_notifications_for_staff(staff_id)

    def submit_shift_change_request(self, staff_id, shift_id, new_start, new_end, reason):
        if not all([shift_id, new_start, new_end, reason]):
            return "❌ All fields are required."
        database.insert_shift_change_request(staff_id, shift_id, new_start, new_end, reason)
        return "✅ Shift change request submitted."

    def get_all_shift_change_requests(self):
        return database.get_all_shift_change_requests()

    def update_shift_change_status(self, request_id, new_status):
        return database.update_shift_change_status(request_id, new_status)
