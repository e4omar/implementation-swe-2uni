from django.db import models

class Staff(models.Model):
    staff_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=[('staff', 'Staff'), ('manager', 'Manager')])
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)  # Consider hashing in production
