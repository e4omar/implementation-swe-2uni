class ScheduleDatabase:
    def __init__(self):
        self.staff_schedules = []
        self.time_off_requests = []
        self.shift_change_requests = []
        self.users = [
            {"username": "alice", "password": "pass123", "role": "staff", "staff_id": "S101", "name": "Alice"},
            {"username": "bob", "password": "admin456", "role": "manager", "staff_id": "M201", "name": "Bob"}
        ]

    def store_time_off_request(self, request):
        self.time_off_requests.append(request)

    def authenticate(self, username, password):
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return user
        return None

