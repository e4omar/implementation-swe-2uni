from server.controller import ScheduleController
from server import database  # only needed for things like add_notification

class ScheduleFacade:
    def __init__(self):
        self.controller = ScheduleController()

    def login(self, username, password):
        return self.controller.login(username, password)

    def submit_time_off(self, staff_id, start_date, end_date, reason):
        return self.controller.submit_time_off_request(staff_id, start_date, end_date, reason)

    def view_schedule(self, staff_id):
        return self.controller.view_schedule(staff_id)

    def get_notifications(self, staff_id):
        return self.controller.get_notifications(staff_id)

    def create_schedule(self, staff_id, date, start_time, end_time):
        return self.controller.create_schedule(staff_id, date, start_time, end_time)

    def view_all_time_off_requests(self):
        return self.controller.get_all_time_off_requests()

    def update_time_off_status(self, request_id, new_status, staff_id):
        success = self.controller.update_shift_change_status(request_id, new_status)
        if success:
            note = f"Your shift-change request (ID: {request_id}) was {new_status}."
            database.add_notification(staff_id, note)
            return "✅ Status updated."
        else:
            return "❌ Request not found."

    def submit_shift_change(self, staff_id, shift_id, new_start, new_end, reason):
        return self.controller.submit_shift_change_request(staff_id, shift_id, new_start, new_end, reason)

    def view_all_shift_change_requests(self):
        return self.controller.get_all_shift_change_requests()

    def update_shift_change_status(self, request_id, new_status, staff_id):
        success = self.controller.update_shift_change_status(request_id, new_status)
        if success:
            note = f"Your shift-change request (ID: {request_id}) was {new_status}."
            database.add_notification(staff_id, note)
            return "✅ Status updated."
        else:
            return "❌ Request not found."

