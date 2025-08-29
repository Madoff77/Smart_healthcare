from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
# on enregistre les ViewSets au niveau projet
from appointments.views import AppointmentViewSet
from patients.views import PatientViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # API
    path('api/', include('patients.urls')),
    path('api/', include('appointments.urls')),
    path('api/', include('symptoms.urls')),     

    # HTML
    path('', include('appointments.urls_html')),
    path('', include('symptoms.urls_html')),


    path('accounts/', include('accounts.urls')),
    
    # Auth (login/logout/password reset prêt à l'emploi)
    path('accounts/', include('django.contrib.auth.urls')),

    # Accueil
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
        
   

]