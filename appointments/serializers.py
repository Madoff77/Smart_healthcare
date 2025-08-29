from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_name', 'patient', 'patient_name',
            'start_time', 'end_time', 'reason', 'status'
        ]
        read_only_fields = []

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name() if obj.doctor else None

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name() if obj.patient else None

    def validate(self, attrs):
        # Laisse le modèle faire la validation d'overlap via clean(), mais on peut ajouter des règles métier ici
        return super().validate(attrs)