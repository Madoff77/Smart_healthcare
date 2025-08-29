from django.contrib import admin
from .models import Symptom

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("patient", "severity", "created_at")
    list_filter = ("severity",)
    search_fields = ("patient__user__username", "patient__user__first_name", "patient__user__last_name", "description")
    date_hierarchy = 'created_at'