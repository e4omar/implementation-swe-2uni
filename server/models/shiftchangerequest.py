class ShiftChangeRequest:
    def __init__(self, request_id, shift_id, staff_id, start_time, end_time, reason, status="Pending"):
        self.request_id = request_id
        self.shift_id = shift_id
        self.staff_id = staff_id
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason
        self.status = status

