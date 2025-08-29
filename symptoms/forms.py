from django import forms
from .models import Symptom

class SymptomCreateForm(forms.ModelForm):
    class Meta:
        model = Symptom
        fields = ["description", "severity"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Décrivez vos symptômes…"}),
        }