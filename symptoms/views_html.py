# symptoms/views_html.py

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .forms import SymptomCreateForm
from .models import Symptom


@login_required
@require_http_methods(["GET", "POST"])  # éditer un symptôme (patient seulement)
def edit_symptom(request, pk: int):
    if not getattr(request.user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    obj = get_object_or_404(Symptom, pk=pk, patient__user=request.user)

    if request.method == 'POST':
        form = SymptomCreateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('symptoms_html:my_symptoms')
    else:
        form = SymptomCreateForm(instance=obj)
    return render(request, 'symptoms/edit.html', {"form": form, "item": obj})


@login_required
@require_http_methods(["GET", "POST"])  # suppression avec page de confirmation
def delete_symptom(request, pk: int):
    if not getattr(request.user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    obj = get_object_or_404(Symptom, pk=pk, patient__user=request.user)

    if request.method == 'POST':
        obj.delete()
        return redirect('symptoms_html:my_symptoms')
    return render(request, 'symptoms/confirm_delete.html', {"item": obj})


@login_required
def my_symptoms(request):
    if not getattr(request.user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")
    qs = Symptom.objects.filter(patient__user=request.user)
    q = request.GET.get('q')
    sev = request.GET.get('severity')
    if q:
        qs = qs.filter(Q(description__icontains=q))
    if sev:
        qs = qs.filter(severity=sev)
    items = qs.order_by('-created_at')
    return render(request, 'symptoms/my.html', {"items": items, "q": q or '', "severity": sev or ''})


@login_required
def doctor_symptoms(request):
    if not getattr(request.user, 'is_doctor', False):
        raise PermissionDenied("Réservé aux médecins.")
    qs = Symptom.objects.filter(
        patient__primary_doctor__user=request.user
    ).select_related('patient__user')
    q = request.GET.get('q')
    sev = request.GET.get('severity')
    if q:
        qs = qs.filter(
            Q(description__icontains=q) |
            Q(patient__user__first_name__icontains=q) |
            Q(patient__user__last_name__icontains=q)
        )
    if sev:
        qs = qs.filter(severity=sev)
    items = qs.order_by('-created_at')
    return render(request, 'symptoms/doctor_list.html', {"items": items, "q": q or '', "severity": sev or ''})


@login_required
def new_symptom(request):
    user = request.user
    if not getattr(user, 'is_patient', False):
        raise PermissionDenied("Réservé aux patients.")

    if request.method == 'POST':
        # throttle simple : 1 ajout / 60s
        last = Symptom.objects.filter(patient__user=user).order_by('-created_at').first()
        if last and (timezone.now() - last.created_at).total_seconds() < 60:
            form = SymptomCreateForm(request.POST)
            form.add_error(None, "Veuillez patienter une minute avant d'ajouter un nouveau symptôme.")
        else:
            form = SymptomCreateForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.patient = user.patient
                obj.save()
                return redirect('symptoms_html:my_symptoms')
    else:
        form = SymptomCreateForm()
    return render(request, 'symptoms/new.html', {"form": form})
