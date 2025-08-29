from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Appointment


def _name(u):
    return u.get_full_name() or u.username


@receiver(pre_save, sender=Appointment)
def cache_previous_status(sender, instance: Appointment, **kwargs):
    """Mémorise l'ancien statut pour détecter les transitions dans post_save."""
    if instance.pk:
        try:
            old = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = old.status
        except Appointment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Appointment)
def notify_on_events(sender, instance: Appointment, created, **kwargs):
    patient_email = instance.patient.user.email or None
    doctor_email = instance.doctor.user.email or None
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    if created:
        subject = "[SmartCare] Nouvelle demande de rendez-vous"
        body = (
            f"""Bonjour {_name(instance.doctor.user)}

"""
            f"""Un nouveau rendez-vous a été demandé par {_name(instance.patient.user)}.
"""
            f"""Date/Heure : {instance.start_time:%d/%m/%Y %H:%M} → {instance.end_time:%H:%M}
"""
            f"""Motif : {instance.reason or '—'}
"""
        )
        if doctor_email:
            send_mail(subject, body, from_email, [doctor_email], fail_silently=True)
        return

    # Mises à jour : transitions de statut
    prev = getattr(instance, '_previous_status', None)
    now = instance.status
    if prev == now:
        return

    if now == Appointment.Status.CONFIRMED:
        subject = "[SmartCare] Rendez-vous confirmé"
        body = (
            f"""Bonjour {_name(instance.patient.user)}

"""
            f"""Votre rendez-vous avec {_name(instance.doctor.user)} est confirmé.
"""
            f"""Date/Heure : {instance.start_time:%d/%m/%Y %H:%M} → {instance.end_time:%H:%M}
"""
        )
        if patient_email:
            send_mail(subject, body, from_email, [patient_email], fail_silently=True)

    elif now == Appointment.Status.CANCELED:
        subject = "[SmartCare] Rendez-vous annulé"
        body = (
            f"""Bonjour,

"""
            f"""Le rendez-vous ({instance.start_time:%d/%m/%Y %H:%M}) a été annulé.
"""
        )
        recipients = [e for e in [patient_email, doctor_email] if e]
        if recipients:
            send_mail(subject, body, from_email, recipients, fail_silently=True)