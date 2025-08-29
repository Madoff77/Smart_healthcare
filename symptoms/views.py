from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Symptom
from .serializers import SymptomSerializer

class SymptomViewSet(viewsets.ModelViewSet):
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Symptom.objects.none()
        if getattr(user, 'is_admin', False):
            return Symptom.objects.all()
        if getattr(user, 'is_doctor', False):
            # Symptômes des patients dont il est le médecin principal
            return Symptom.objects.filter(patient__primary_doctor__user=user)
        # patient
        return Symptom.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'is_patient', False):
            return serializer.save(patient=user.patient)
        if getattr(user, 'is_doctor', False) or getattr(user, 'is_admin', False):
            return serializer.save()
        raise PermissionDenied("Accès refusé.")
    
    def perform_update(self, serializer):
        user = self.request.user
        obj = self.get_object()
        if getattr(user, 'is_admin', False):
            return serializer.save()
        # patient : ne peut éditer que ses propres symptômes
        if getattr(user, 'is_patient', False) and obj.patient.user == user:
            return serializer.save()
        # médecin : lecture seule via API (peut être assoupli plus tard)
        raise PermissionDenied("Modification interdite.")

    def perform_destroy(self, instance):
        user = self.request.user
        if getattr(user, 'is_admin', False):
            return instance.delete()
        if getattr(user, 'is_patient', False) and instance.patient.user == user:
            return instance.delete()
        raise PermissionDenied("Suppression interdite.")