import json
import os
from server.models.timeoffrequest import TimeOffRequest
from server.models.shiftchangerequest import ShiftChangeRequest

class ScheduleDatabase:
    def __init__(self):
        self.staff_schedules = []
        self.time_off_requests = []
        self.shift_change_requests = []
        self.users = [
            {"username": "alice", "password": "pass123", "role": "staff", "staff_id": "S101", "name": "Alice"},
            {"username": "bob", "password": "admin456", "role": "manager", "staff_id": "M201", "name": "Bob"}
        ]
        self.load_requests()
        self.load_shift_change_requests()

    # ──────────────── AUTH ────────────────
    def authenticate(self, username, password):
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return user
        return None

    # ──────────────── TIME-OFF REQUESTS ────────────────
    def store_time_off_request(self, request):
        self.time_off_requests.append(request)
        self.save_requests()

    def get_all_time_off_requests(self):
        return self.time_off_requests

    def save_requests(self):
        data = [{
            "request_id": r.request_id,
            "staff_id": r.staff_id,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "reason": r.reason
        } for r in self.time_off_requests]

        with open("time_off_requests.json", "w") as f:
            json.dump(data, f)

    def load_requests(self):
        if os.path.exists("time_off_requests.json"):
            with open("time_off_requests.json", "r") as f:
                data = json.load(f)
                for item in data:
                    request = TimeOffRequest(
                        item["request_id"],
                        item["staff_id"],
                        item["start_date"],
                        item["end_date"],
                        item["reason"]
                    )
                    self.time_off_requests.append(request)

    # ──────────────── SHIFT-CHANGE REQUESTS ────────────────
    def store_shift_change_request(self, request):
        self.shift_change_requests.append(request)
        self.save_shift_change_requests()

    def get_all_shift_change_requests(self):
        return self.shift_change_requests

    def save_shift_change_requests(self):
        data = [{
            "request_id": r.request_id,
            "shift_id": r.shift_id,
            "staff_id": r.staff_id,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "reason": r.reason
        } for r in self.shift_change_requests]

        with open("shift_change_requests.json", "w") as f:
            json.dump(data, f)

    def load_shift_change_requests(self):
        if os.path.exists("shift_change_requests.json"):
            with open("shift_change_requests.json", "r") as f:
                data = json.load(f)
                for item in data:
                    request = ShiftChangeRequest(
                        item["request_id"],
                        item["shift_id"],
                        item["staff_id"],
                        item["start_time"],
                        item["end_time"],
                        item["reason"]
                    )
                    self.shift_change_requests.append(request)


     
       
   
   
      


