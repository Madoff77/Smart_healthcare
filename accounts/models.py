from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        DOCTOR = 'doctor', 'Médecin'
        PATIENT = 'patient', 'Patient'


    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.PATIENT)


    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN


    @property
    def is_doctor(self):
        return self.role == self.Roles.DOCTOR


    @property
    def is_patient(self):
        return self.role == self.Roles.PATIENT          

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Roles.DOCTOR})
    specialty = models.CharField(max_length=120, blank=True)
    office_address = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return f"Dr {self.user.get_full_name()}" if self.user.get_full_name() else f"Dr {self.user.username}"