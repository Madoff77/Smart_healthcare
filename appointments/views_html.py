from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.http import require_POST

from .forms import AppointmentCreateForm, AppointmentDoctorUpdateForm
from .models import Appointment


# --- Helpers simples pour l'UX (pas besoin de modifier le modèle) ---
def _can_cancel(appt):
    # Annulation possible si pas annulé et si le RDV n'a pas démarré
    if appt.status == Appointment.Status.CANCELED:
        return False
    return appt.start_time > timezone.now()


def _can_manage(appt):
    # Gestion possible si non annulé et futur
    if appt.status == Appointment.Status.CANCELED:
        return False
    return appt.start_time > timezone.now()


# --- Vues Patient ---
@login_required
def create_for_self(request):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")

    if request.method == 'POST':
        form = AppointmentCreateForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = user.patient
            appt.status = Appointment.Status.PENDING
            # Rendre aware si besoin
            for field in ("start_time", "end_time"):
                val = getattr(appt, field)
                if isinstance(val, datetime) and val.tzinfo is None:
                    setattr(appt, field, make_aware(val))
            appt.save()  # déclenche clean() anti-chevauchement
            messages.success(request, "Votre demande de rendez-vous a été enregistrée (en attente).")
            return redirect('appointments_html:new_success')
    else:
        form = AppointmentCreateForm()
    return render(request, 'appointments/new.html', {"form": form})


@login_required
def new_success(request):
    return render(request, 'appointments/new_success.html')


@login_required
def patient_my_appointments(request):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    appts = Appointment.objects.filter(patient__user=user).order_by('-start_time')

    # ajoute un attribut can_cancel pour l’UX du template
    for a in appts:
        a.can_cancel = _can_cancel(a)

    return render(request, 'appointments/my_patient.html', {"appts": appts})


@login_required
@require_POST
def cancel_own(request, pk: int):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    appt = get_object_or_404(Appointment, pk=pk, patient__user=user)

    if not _can_cancel(appt):
        raise PermissionDenied("Ce rendez-vous ne peut plus être annulé.")

    appt.status = Appointment.Status.CANCELED
    appt.save()
    messages.success(request, "Rendez-vous annulé.")
    return redirect('appointments_html:patient_my')


# --- Vues Médecin ---
@login_required
def doctor_my_appointments(request):
    user = request.user
    if not getattr(user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")
    appts = Appointment.objects.filter(doctor__user=user).order_by('-start_time')

    # ajoute un attribut can_manage pour l’UX du template
    for a in appts:
        a.can_manage = _can_manage(a)

    return render(request, 'appointments/my_doctor.html', {"appts": appts})


@login_required
def doctor_manage(request, pk: int):
    user = request.user
    if not getattr(user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")

    appt = get_object_or_404(Appointment, pk=pk)
    if appt.doctor.user != user:
        raise PermissionDenied("Vous ne pouvez gérer que vos rendez-vous.")

    can_manage = _can_manage(appt)

    if request.method == 'POST':
        if not can_manage:
            raise PermissionDenied("Ce rendez-vous ne peut plus être modifié.")
        form = AppointmentDoctorUpdateForm(request.POST, instance=appt)
        if form.is_valid():
            obj = form.save(commit=False)
            # awareness timezone si besoin
            for field in ("start_time", "end_time"):
                val = getattr(obj, field)
                if isinstance(val, datetime) and val.tzinfo is None:
                    setattr(obj, field, make_aware(val))
            obj.save()
            messages.success(request, "Rendez-vous mis à jour avec succès.")
            return redirect('appointments_html:manage', pk=appt.pk)
    else:
        form = AppointmentDoctorUpdateForm(instance=appt)

    return render(request, 'appointments/manage.html', {"form": form, "appt": appt, "can_manage": can_manage})
