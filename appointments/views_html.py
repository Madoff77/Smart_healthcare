from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import datetime
from django.views.decorators.http import require_POST

from .models import Appointment
from .forms import AppointmentCreateForm, AppointmentDoctorUpdateForm


@login_required
def create_for_self(request):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")

    if request.method == 'POST':
        form = AppointmentCreateForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            # Forcer patient et statut
            appt.patient = user.patient
            appt.status = Appointment.Status.PENDING
            # Si le navigateur envoie des datetime naïfs, on les rend aware
            for field in ("start_time", "end_time"):
                val = getattr(appt, field)
                if isinstance(val, datetime) and val.tzinfo is None:
                    setattr(appt, field, make_aware(val))
            appt.save()  # déclenche clean() (anti-chevauchement)
            return redirect('appointments_html:new_success')
    else:
        form = AppointmentCreateForm()
    return render(request, 'appointments/new.html', {"form": form})


@login_required
def new_success(request):
    return render(request, 'appointments/new_success.html')


@login_required
def doctor_manage(request, pk: int):
    user = request.user
    if not getattr(user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")

    appt = get_object_or_404(Appointment, pk=pk)
    if appt.doctor.user != user:
        raise PermissionDenied("Vous ne pouvez gérer que vos rendez-vous.")

    # Autoriser la gestion seulement si non annulé et futur
    can_manage = (appt.status != Appointment.Status.CANCELED and appt.start_time > timezone.now())

    if request.method == 'POST':
        if not can_manage:
            raise PermissionDenied("Ce rendez-vous ne peut plus être modifié.")
        form = AppointmentDoctorUpdateForm(request.POST, instance=appt)
        if form.is_valid():
            obj = form.save(commit=False)
            # Si datetime naïfs, on les rend aware
            for field in ("start_time", "end_time"):
                val = getattr(obj, field)
                if isinstance(val, datetime) and val.tzinfo is None:
                    setattr(obj, field, make_aware(val))
            obj.save()
            return redirect('appointments_html:manage', pk=appt.pk)
    else:
        form = AppointmentDoctorUpdateForm(instance=appt)

    return render(request, 'appointments/manage.html', {"form": form, "appt": appt, "can_manage": can_manage})


@login_required
def patient_my_appointments(request):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    appts = Appointment.objects.filter(patient__user=user).order_by('-start_time')
    now = timezone.now()
    for a in appts:
        a.can_cancel = (a.status == Appointment.Status.PENDING and a.start_time > now)
    return render(request, 'appointments/my_patient.html', {"appts": appts})


@login_required
def doctor_my_appointments(request):
    user = request.user
    if not getattr(user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")
    appts = Appointment.objects.filter(doctor__user=user).order_by('-start_time')
    now = timezone.now()
    for a in appts:
        a.can_manage = (a.status != Appointment.Status.CANCELED and a.start_time > now)
    return render(request, 'appointments/my_doctor.html', {"appts": appts})


@login_required
@require_POST
def cancel_own(request, pk: int):
    """Un patient annule son propre RDV depuis la liste."""
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    appt = get_object_or_404(Appointment, pk=pk, patient__user=user)
    # Autoriser annulation seulement si PENDING et futur
    if appt.status != Appointment.Status.PENDING or appt.start_time <= timezone.now():
        raise PermissionDenied("Ce rendez-vous ne peut plus être annulé.")
    appt.status = Appointment.Status.CANCELED
    appt.save()
    return redirect('appointments_html:patient_my')