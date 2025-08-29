from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Symptom


def _name(u):
    return u.get_full_name() or u.username

@receiver(post_save, sender=Symptom)
def notify_doctor_on_new_symptom(sender, instance: Symptom, created, **kwargs):
    if not created:
        return
    patient = instance.patient
    doctor = patient.primary_doctor
    if not doctor or not doctor.user.email:
        return

    urgent = (instance.severity == Symptom.Severity.SEVERE)
    subject = "[SmartCare] Nouveau symptôme ajouté par un patient"
    body = (
        f"""Bonjour {_name(doctor.user)}

"""
        f"""Le patient {_name(patient.user)} a ajouté un symptôme :
"""
        f"""- Date/Heure : {instance.created_at:%d/%m/%Y %H:%M}
"""
        f"""- Sévérité : {instance.get_severity_display() if instance.severity else '—'}
"""
        f"""- Description : {instance.description}
"""
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    send_mail(subject, body, from_email, [doctor.user.email], fail_silently=True)