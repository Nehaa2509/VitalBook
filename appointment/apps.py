from django.apps import AppConfig


class AppointmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointment'
    verbose_name = 'VitalBook Platform'

    def ready(self):
        import appointment.signals  # noqa: F401 — registers signal handlers
