"""
WSGI config for Lost_Found project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lost_Found.settings')

application = get_wsgi_application()

try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('init_admin', interactive=False)
    print("WSGI database migrations and init_admin executed successfully.")
except Exception as err:
    print(f"WSGI auto-migration notice: {err}")

