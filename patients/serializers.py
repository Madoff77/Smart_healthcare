from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)
    primary_doctor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'user_name', 'age', 'medical_history',
            'primary_doctor', 'primary_doctor_name'
        ]
        read_only_fields = ['user']  # le patient ne change pas son user via l'API

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_primary_doctor_name(self, obj):
        return obj.primary_doctor.user.get_full_name() if obj.primary_doctor else None