import os
import sys
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key')

DEBUG = os.environ.get('DEBUG', '1') == '1'

# Better parsing for ALLOWED_HOSTS to handle empty strings and wildcards
allowed_hosts_raw = os.environ.get('ALLOWED_HOSTS', '').strip()
if allowed_hosts_raw:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.run.app', '.a.run.app']

# Trust Cloud Run's proxy
CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.a.run.app',
]

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_htmx',
    'storages',
    'web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'toxic_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.context_processors.footer_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'toxic_project.wsgi.application'

# Database
# Use DATABASE_URL env var if available (Docker), otherwise SQLite (Local)
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration (handled by Whitenoise in production)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'web' / 'static',
    BASE_DIR / 'static',
]

# Use Whitenoise for static files without crashing on missing manifest entries (~images not committed)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------------------
# Google Cloud Storage for media files (production)
# When GCS_BUCKET_NAME is set, uploaded files go to Cloud Storage.
# Falls back to local media/ in development.
# ---------------------------------------------------------------------------
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', '').strip()
if GCS_BUCKET_NAME:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
    GS_BUCKET_NAME = GCS_BUCKET_NAME
    GS_DEFAULT_ACL = None  # Use bucket-level IAM, not per-object ACLs
    GS_QUERYSTRING_AUTH = False  # Public bucket — no signed URLs needed
    MEDIA_URL = f'https://storage.googleapis.com/{GCS_BUCKET_NAME}/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings (production)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

UNFOLD = {
    "COLORS": {
        "primary": {
            "50": "255 241 242",
            "100": "255 228 230",
            "200": "254 205 211",
            "300": "253 164 175",
            "400": "251 113 133",
            "500": "244 63 94",
            "600": "225 29 72",
            "700": "190 18 60",
            "800": "159 18 57",
            "900": "136 19 55",
            "950": "76 5 25",
        },
    },
}

# ---------------------------------------------------------------------------
# Content Security Policy (django-csp)
# ---------------------------------------------------------------------------
# Allows: own origin, YouTube iframes, Google Fonts, HTMX CDN.
# Inline styles/scripts are blocked — use external files or nonces if needed.
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://unpkg.com",           # HTMX
    "https://www.youtube.com",
    "https://s.ytimg.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "https://fonts.googleapis.com",
    "'unsafe-inline'",             # Tailwind generates inline styles; remove once migrated
)
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https:",                       # Allow images from any HTTPS source (CDN, YouTube thumbnails)
)
CSP_FRAME_SRC = (
    "'self'",
    "https://www.youtube.com",
    "https://www.youtube-nocookie.com",
    "https://www.facebook.com",
)
CSP_CONNECT_SRC = ("'self'",)
CSP_MEDIA_SRC = ("'self'",)
# Report violations to the console (set CSP_REPORT_URI for a real endpoint)
CSP_REPORT_ONLY = False

import sys

# Redis Caching (fall back to LocMemCache or DummyCache if Redis is not configured)
redis_url = os.environ.get('REDIS_URL')

if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
elif redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': redis_url,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'toxic-cache',
        }
    }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'] if DEBUG else ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'web': {
            'handlers': ['console', 'file'] if DEBUG else ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Production environment variable validation
# ---------------------------------------------------------------------------
# Handled by resilient defaults above.
