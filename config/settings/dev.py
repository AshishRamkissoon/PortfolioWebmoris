from .base import *

DEBUG = env.bool("DEBUG", default=True)
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-only-not-for-production")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

MAILERS = {"default": {"BACKEND": "django.core.mail.backends.console.EmailBackend"}}

# runserver serves static files itself; no collectstatic/manifest needed while developing.
MIDDLEWARE.remove("whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
