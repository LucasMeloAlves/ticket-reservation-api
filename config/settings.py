"""
Impostazioni del progetto "Ticket Reservation API".

Progetto Backend PPM 2026 - traccia 4 (REST API per prenotazione biglietti).
Framework: Django + Django REST Framework, con login tramite token JWT.
Database: SQLite (il file db.sqlite3 e' gia' incluso e pieno di dati demo).

Qui dentro si configura tutto: app usate, database, sicurezza, ecc.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Sicurezza
# ---------------------------------------------------------------------------
# Chiave segreta di Django. In locale va bene questa; online (Render) se ne usa
# una vera passata come variabile d'ambiente DJANGO_SECRET_KEY.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-demo-key-change-me-in-production-0123456789",
)

# DEBUG acceso in locale (mostra gli errori); si spegne online mettendo DJANGO_DEBUG=0.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Indirizzi da cui l'app puo' essere raggiunta. Su Render l'indirizzo pubblico
# arriva automaticamente nella variabile RENDER_EXTERNAL_HOSTNAME.
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)
_extra_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
if _extra_hosts:
    ALLOWED_HOSTS.extend(h.strip() for h in _extra_hosts.split(",") if h.strip())

CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")

# ---------------------------------------------------------------------------
# App installate
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Librerie esterne
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # Le mie due app
    "accounts",  # utenti e login
    "events",    # eventi e prenotazioni
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# In locale uso il file SQLite db.sqlite3 (gia' incluso e pieno di dati).
# Se e' impostata la variabile DATABASE_URL (es. un Postgres online) uso quella.
# NOTA: per il caso locale NON passo un URL "sqlite://" alla libreria, perche'
# se il percorso contiene spazi (come "Backend PPM") l'URL si rompe e Django
# finirebbe per usare un database vuoto.
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Regole per le password (lunghezza minima, non troppo comuni, ecc.)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

# ---------------------------------------------------------------------------
# Lingua e fuso orario
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# File statici (gestiti da WhiteNoise, utile per il deploy online)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Configurazione dell'API (Django REST Framework) e del login JWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Come si riconosce l'utente: tramite token JWT.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Regola di base: chi non e' loggato puo' solo leggere.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    # Divido le liste lunghe in pagine da 20 elementi.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# Durata dei token: l'access dura 6 ore, il refresh 1 giorno.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# CORS: permette a un sito/client esterno di chiamare l'API.
# Per la demo lascio aperto a tutti.
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
