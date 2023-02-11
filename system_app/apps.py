from django.apps import AppConfig
from django.db.models.signals import post_save


class SystemAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system_app'

    # def ready(self) -> None:
    #     from . import signals
    #
