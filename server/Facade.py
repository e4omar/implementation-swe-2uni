from server.controller import ScheduleController
from server.database import ScheduleDatabase

class ScheduleFacade:
    def __init__(self):
        self.db = ScheduleDatabase()
        self.controller = ScheduleController(self.db)

    def create_staff_schedule(self, staff_id, date, start_time, end_time):
        return self.controller.create_schedule(staff_id, date, start_time, end_time)

    def submit_time_off(self, request_id, staff_id, start_date, end_date, reason):
        return self.controller.request_time_off(request_id, staff_id, start_date, end_date, reason)

    def submit_shift_change(self, request_id, shift_id, staff_id, start_time, end_time, reason):
        return self.controller.request_shift_change(request_id, shift_id, staff_id, start_time, end_time, reason)
