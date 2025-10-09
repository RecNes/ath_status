from django.apps import AppConfig


class AllTimeHighConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "all_time_high"

    def ready(self):
        import all_time_high.signals
