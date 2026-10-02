import sys
from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        # Avoid running during management commands like collectstatic, makemigrations, check
        if any(cmd in sys.argv for cmd in ['collectstatic', 'makemigrations', 'check', 'test']):
            return

        try:
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            call_command('init_admin', interactive=False)
        except Exception as e:
            print(f"Startup migration notice: {e}")

