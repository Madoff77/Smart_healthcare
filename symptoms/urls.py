from rest_framework.routers import DefaultRouter
from .views import SymptomViewSet

router = DefaultRouter()
router.register(r'symptoms', SymptomViewSet, basename='symptom')

urlpatterns = router.urls