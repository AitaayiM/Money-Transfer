from django.apps import AppConfig
# Importation relative

class IdentitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'identities'

    def ready(self):
        from . import signals
