from django.urls import path
from . import views_html

app_name = 'appointments_html'

urlpatterns = [
    path('appointments/new/', views_html.create_for_self, name='new'),
    path('appointments/new/success/', views_html.new_success, name='new_success'),
    path('appointments/<int:pk>/manage/', views_html.doctor_manage, name='manage'),

    # Mes rendez-vous
    path('me/appointments/', views_html.patient_my_appointments, name='patient_my'),
    path('doctor/appointments/', views_html.doctor_my_appointments, name='doctor_my'),
    path('appointments/<int:pk>/cancel/', views_html.cancel_own, name='cancel_own'),
]