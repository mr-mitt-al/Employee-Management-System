from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .manager import EmployeeManager


class Employee(AbstractUser):
    """
    Creating an Employee model where phone_number,profile_picture
    and description are the optional fields and rest all are mandatory.
    """
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    position = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    hiring_date = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='employeeProfile/')

    USERNAME_FIELD = 'email'
    # email will be used for login operation rather than username
    REQUIRED_FIELDS = ['first_name', 'last_name', 'age', 'position']

    objects = EmployeeManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class RequestLeave(models.Model):
    """
    Creating a leave request model which has relation with Employee model
    where reason and attached_file are optional fields rest all are mandatory
    fields
    """
    LEAVE_CHOICES = [("approved", "Approved"), ("pending", "Pending"), ("rejected", "Rejected")]
    # Choices for leaves that admin would have and by default it is in pending state
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="user_leaves")
    reason = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_requested_at = models.DateTimeField(default=timezone.now)
    leave_status = models.CharField(max_length=8, choices=LEAVE_CHOICES, default="pending")
    attached_file = models.FileField(null=True, blank=True, upload_to='attached_files/')

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} leave={self.leave_status}"