from django.db import models
from django.conf import settings
from accounts.models import Doctor


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    age = models.PositiveIntegerField(null=True, blank=True)
    medical_history = models.TextField(blank=True)  # antécédents
    primary_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_patients')


    def __str__(self):
        return self.user.get_full_name() or self.user.username