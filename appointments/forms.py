from django import forms
from .models import Appointment

# Widget HTML5 correct pour datetime-local (pré-remplit les champs avec le bon format)
class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"
    def __init__(self, **kwargs):
        # Format exigé par <input type="datetime-local"> : 2025-09-01T09:00
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(**kwargs)

DT_LOCAL_INPUT_FORMATS = ["%Y-%m-%dT%H:%M"]

class AppointmentCreateForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=DateTimeLocalInput(), input_formats=DT_LOCAL_INPUT_FORMATS)
    end_time = forms.DateTimeField(widget=DateTimeLocalInput(), input_formats=DT_LOCAL_INPUT_FORMATS)

    class Meta:
        model = Appointment
        fields = ["doctor", "start_time", "end_time", "reason"]  # patient/status gérés par la vue
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
        }

class AppointmentDoctorUpdateForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=DateTimeLocalInput(), input_formats=DT_LOCAL_INPUT_FORMATS)
    end_time = forms.DateTimeField(widget=DateTimeLocalInput(), input_formats=DT_LOCAL_INPUT_FORMATS)

    class Meta:
        model = Appointment
        fields = ["start_time", "end_time", "reason", "status"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
        }
