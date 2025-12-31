from django.apps import AppConfig


class CivicSaathiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "civic_saathi"
    
    def ready(self):
        """Import signals when the app is ready"""
        import civic_saathi.signals  # noqa
