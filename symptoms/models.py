from django.db import models
from patients.models import Patient

class Symptom(models.Model):
    class Severity(models.TextChoices):
        MILD = 'mild', 'Léger'
        MODERATE = 'moderate', 'Modéré'
        SEVERE = 'severe', 'Sévère'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='symptoms')
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Symptôme de {self.patient.user.get_full_name() or self.patient.user.username} – {self.created_at:%Y-%m-%d %H:%M}"