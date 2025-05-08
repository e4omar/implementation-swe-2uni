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
        self.notifications = {}  # {staff_id: [messages]}
        self.load_notifications()


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
            "reason": r.reason,
            "status": r.status
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
                        item["reason"],
                        item.get("status", "Pending")
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
                        item["reason"],
                        item.get("status", "Pending")
                    )
                    self.shift_change_requests.append(request)

    def update_time_off_status(self, request_id, new_status):
        for r in self.time_off_requests:
            if r.request_id == request_id:
                r.status = new_status
                self.save_requests()
                return True
        return False

    def update_shift_change_status(self, request_id, new_status):
        for r in self.shift_change_requests:
            if r.request_id == request_id:
                r.status = new_status
                self.save_shift_change_requests()
                return True
        return False

    def add_notification(self, staff_id, message):
        if staff_id not in self.notifications:
            self.notifications[staff_id] = []
        self.notifications[staff_id].append(message)
        self.save_notifications()

    def get_notifications(self, staff_id):
        return self.notifications.get(staff_id, [])

    def save_notifications(self):
        with open("notifications.json", "w") as f:
            json.dump(self.notifications, f)

    def load_notifications(self):
        if os.path.exists("notifications.json"):
            with open("notifications.json", "r") as f:
                self.notifications = json.load(f)



     
       
   
   
      


