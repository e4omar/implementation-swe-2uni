class Staff:
    def __init__(self, staff_id, name, username, password, role="staff"):
        self.staff_id = staff_id
        self.name = name
        self.username = username
        self.password = password
        self.role = role  # "staff" or "manager"
