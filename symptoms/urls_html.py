from django.urls import path

from symptoms import views_export
from . import views_html

app_name = 'symptoms_html'

urlpatterns = [
    path('symptoms/new/', views_html.new_symptom, name='new_symptom'),
    path('me/symptoms/', views_html.my_symptoms, name='my_symptoms'),
    path('symptoms/<int:pk>/edit/', views_html.edit_symptom, name='edit_symptom'),
    path('symptoms/<int:pk>/delete/', views_html.delete_symptom, name='delete_symptom'),
    path('doctor/symptoms/', views_html.doctor_symptoms, name='doctor_symptoms'),
    path('me/symptoms/export.csv', views_export.export_my_symptoms_csv, name='export_my_symptoms_csv'),
    path('doctor/symptoms/export.csv', views_export.export_doctor_symptoms_csv, name='export_doctor_symptoms_csv'),
]