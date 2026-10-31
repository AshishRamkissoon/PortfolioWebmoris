from .base import *

DEBUG = False
SECRET_KEY = env("SECRET_KEY")  # required: fails loudly if missing
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # required
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# HTTPS everywhere
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31_536_000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# EMAIL_URL, e.g. smtp+tls://user:password@smtp.example.com:587
_email = env.email_url("EMAIL_URL")  # required: lead and order emails must not be dropped
_smtp = "smtp" in _email["EMAIL_BACKEND"]
MAILERS = {
    "default": {
        "BACKEND": _email["EMAIL_BACKEND"],
        "OPTIONS": {
            "host": _email["EMAIL_HOST"],
            "port": _email["EMAIL_PORT"] or None,
            "username": _email["EMAIL_HOST_USER"],
            "password": _email["EMAIL_HOST_PASSWORD"],
            "use_tls": _email.get("EMAIL_USE_TLS", False),
            "use_ssl": _email.get("EMAIL_USE_SSL", False),
            "timeout": 10,
        }
        if _smtp
        else {},
    }
}

LOGGING["root"]["level"] = "WARNING"
