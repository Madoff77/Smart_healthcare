from django.apps import AppConfig

class SymptomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'symptoms'

    def ready(self):
        import symptoms.signals  # noqa