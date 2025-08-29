from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from patients.models import Patient

User = get_user_model()

class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=False, label='Prénom')
    last_name = forms.CharField(required=False, label='Nom')
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Tague le rôle patient si le modèle User le supporte
        if hasattr(user, 'role'):
            setattr(user, 'role', 'patient')
        elif hasattr(user, 'is_patient'):
            setattr(user, 'is_patient', True)
        if commit:
            user.save()
            # Crée automatiquement le profil Patient
            Patient.objects.get_or_create(user=user)
        return user