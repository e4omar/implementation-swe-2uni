import json
import os
from server.models.timeoffrequest import TimeOffRequest

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
    def authenticate(self, username, password):
        for user in self.users:
            if user["username"].lower() == username.lower() and user["password"] == password:
                return user
        return None
     
       
   
   
      


