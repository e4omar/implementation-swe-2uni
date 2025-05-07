class StaffSchedule:
    def __init__(self, staff_id, date, start_time, end_time):
        self.staff_id = staff_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"<StaffSchedule staff_id={self.staff_id}, date={self.date}, time={self.start_time}-{self.end_time}>"
