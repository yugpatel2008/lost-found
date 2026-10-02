"""
Render WSGI entry point fallback wrapper.
Exposes `app` for `gunicorn app:app`.
"""
from Lost_Found.wsgi import application as app
