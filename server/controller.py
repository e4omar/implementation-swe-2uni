from server.models.schedule import StaffSchedule
from server.models.timeoffrequest import TimeOffRequest
from server.models.shiftchangerequest import ShiftChangeRequest

class ScheduleController:
    def __init__(self, db):
        self.db = db

    def create_schedule(self, staff_id, date, start_time, end_time):
        schedule = StaffSchedule(staff_id, date, start_time, end_time)
        self.db.store_schedule(schedule)
        return f"Schedule created for {staff_id} on {date}"

    def request_time_off(self, request_id, staff_id, start_date, end_date, reason):
        request = TimeOffRequest(request_id, staff_id, start_date, end_date, reason)
        self.db.store_time_off_request(request)
        return "Time-off request submitted."

    def request_shift_change(self, request_id, shift_id, staff_id, start_time, end_time, reason):
        request = ShiftChangeRequest(request_id, shift_id, staff_id, start_time, end_time, reason)
        self.db.store_shift_change_request(request)
        return "Shift change request submitted."
