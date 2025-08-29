from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db.models import Q
import csv

from .models import Symptom

@login_required
def export_my_symptoms_csv(request):
    if not getattr(request.user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    qs = Symptom.objects.filter(patient__user=request.user).order_by('-created_at')
    return _export_symptoms(qs, filename="mes_symptomes.csv")

@login_required
def export_doctor_symptoms_csv(request):
    if not getattr(request.user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")
    qs = Symptom.objects.filter(patient__primary_doctor__user=request.user).select_related('patient__user').order_by('-created_at')
    return _export_symptoms(qs, filename="symptomes_mes_patients.csv", include_patient=True)


def _export_symptoms(qs, filename: str, include_patient: bool = False):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(resp)
    headers = ["date", "severity", "description"]
    if include_patient:
        headers.insert(0, "patient")
    writer.writerow(headers)
    for s in qs:
        row = [s.created_at.strftime('%Y-%m-%d %H:%M'), s.get_severity_display() or '', s.description]
        if include_patient:
            row.insert(0, s.patient.user.get_full_name() or s.patient.user.username)
        writer.writerow(row)
    return resp