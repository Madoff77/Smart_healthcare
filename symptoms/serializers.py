from rest_framework import serializers
from .models import Symptom

class SymptomSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Symptom
        fields = ["id", "patient", "patient_name", "description", "severity", "created_at"]
        read_only_fields = ["patient", "created_at"]

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name() or obj.patient.user.username