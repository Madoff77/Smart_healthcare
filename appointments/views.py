from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Appointment.objects.none()
        if getattr(user, 'is_admin', False):
            return Appointment.objects.all()
        if getattr(user, 'is_doctor', False):
            return Appointment.objects.filter(doctor__user=user)
        # patient
        return Appointment.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        # Patient : création pour soi uniquement, statut forcé à 'pending'
        if getattr(user, 'is_patient', False):
            patient = getattr(user, 'patient', None)
            if not patient:
                raise PermissionDenied("Profil patient introuvable.")
            # On ignore tout 'status' et 'patient' envoyés par le client
            serializer.validated_data.pop('status', None)
            serializer.validated_data.pop('patient', None)
            serializer.save(patient=patient, status=Appointment.Status.PENDING)
            return

        # Médecin/Admin : création libre (les validations restent côté modèle)
        if getattr(user, 'is_doctor', False) or getattr(user, 'is_admin', False):
            serializer.save()
            return

        raise PermissionDenied("Accès refusé.")

    def perform_update(self, serializer):
        user = self.request.user
        appointment = self.get_object()

        # Patient : ne peut que modifier la raison ou annuler son propre RDV
        if getattr(user, 'is_patient', False):
            if appointment.patient.user != user:
                raise PermissionDenied("Accès refusé.")
            allowed_fields = {'reason', 'status'}
            # Retire les champs non autorisés (ex: doctor, times, patient)
            for field in set(serializer.validated_data.keys()) - allowed_fields:
                serializer.validated_data.pop(field, None)
            # Status autorisé uniquement à 'canceled'
            if 'status' in serializer.validated_data and serializer.validated_data['status'] != Appointment.Status.CANCELED:
                raise PermissionDenied("Un patient ne peut que annuler son rendez-vous.")
            serializer.save()
            return

        # Médecin : peut modifier ses propres RDV (heures, statut, raison)
        if getattr(user, 'is_doctor', False):
            if appointment.doctor.user != user:
                raise PermissionDenied("Accès refusé.")
            serializer.save()
            return

        # Admin : tout
        if getattr(user, 'is_admin', False):
            serializer.save()
            return

        raise PermissionDenied("Accès refusé.")