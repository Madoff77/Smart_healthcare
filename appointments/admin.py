from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "start_time", "end_time", "status")
    list_filter = ("status", "doctor")
    search_fields = ("doctor__user__username", "patient__user__username")