class ScheduleDatabase:
    def __init__(self):
        self.staff_schedules = []
        self.time_off_requests = []
        self.shift_change_requests = []

    def store_schedule(self, schedule):
        self.staff_schedules.append(schedule)

    def fetch_schedule_by_staff(self, staff_id):
        return [s for s in self.staff_schedules if s.staff_id == staff_id]

    def store_time_off_request(self, request):
        self.time_off_requests.append(request)

    def store_shift_change_request(self, request):
        self.shift_change_requests.append(request)
