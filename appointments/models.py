from django.db import models
from django.core.exceptions import ValidationError
from grpc import Status
from accounts.models import Doctor
from patients.models import Patient


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmé'
        CANCELED = 'canceled', 'Annulé'


    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)


    class Meta:
        ordering = ['start_time']
        constraints = [
            # Unicité stricte du même créneau (option de sécurité)
            models.UniqueConstraint(fields=['doctor', 'start_time'], name='unique_doctor_start'),
]


    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({'end_time': "L'heure de fin doit être après l'heure de début."})


# Anti-chevauchement pour un même médecin : (A.start < B.end) et (A.end > B.start)
        qs = Appointment.objects.filter(doctor=self.doctor)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        overlap = qs.filter(start_time__lt=self.end_time, end_time__gt=self.start_time).exists()
        if overlap:
            raise ValidationError("Ce créneau chevauche un autre rendez-vous pour ce médecin.")


    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.doctor} · {self.start_time:%Y-%m-%d %H:%M}"