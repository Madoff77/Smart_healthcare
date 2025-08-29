from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Patient.objects.none()
        if getattr(user, 'is_admin', False):
            return Patient.objects.all()
        if getattr(user, 'is_doctor', False):
            # Version simple : patients dont il est médecin principal
            return Patient.objects.filter(primary_doctor__user=user)
        # patient: ne voit que son profil
        return Patient.objects.filter(user=user)

    def perform_create(self, serializer):
        # On limite la création aux admins (création d'un patient via API)
        user = self.request.user
        if not getattr(user, 'is_admin', False):
            raise PermissionDenied("Seul un administrateur peut créer un patient via l'API.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        # Patient peut éditer certaines infos de son profil ?
        if getattr(user, 'is_patient', False) and instance.user != user:
            raise PermissionDenied("Accès refusé.")
        # Médecin peut éditer le dossier médical ? (à ajuster selon politique)
        if getattr(user, 'is_doctor', False):
            # optionnel: restreindre aux patients dont il est le médecin principal
            if instance.primary_doctor and instance.primary_doctor.user != user:
                raise PermissionDenied("Accès refusé.")
        serializer.save()