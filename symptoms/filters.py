import django_filters as df
from .models import Symptom

class SymptomFilter(df.FilterSet):
    created_at = df.IsoDateTimeFromToRangeFilter()
    severity = df.MultipleChoiceFilter(choices=Symptom.Severity.choices)

    class Meta:
        model = Symptom
        fields = ["severity", "created_at", "patient"]