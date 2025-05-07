class TimeOffRequest:
    def __init__(self, request_id, staff_id, start_date, end_date, reason):
        self.request_id = request_id
        self.staff_id = staff_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
