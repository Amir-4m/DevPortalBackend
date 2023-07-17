"""
Base settings to build other settings files upon.
"""
import json
import boto3 as boto3
import environ

from distutils.util import strtobool
from pathlib import Path
from urllib import request
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# devportal/
APPS_DIR = BASE_DIR / "devportal"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))
AWS_ACCOUNT = env.str('AWS_ACCOUNT', default=None)
AWS_REGION = env.str('AWS_REGION', default='ca-central-1')
AWS_SES_REGION_NAME = env.str('AWS_SES_REGION_NAME', default='ca-central-1')
AWS_SES_REGION_ENDPOINT = env.str('AWS_SES_REGION_ENDPOINT', default=f'email.{AWS_SES_REGION_NAME}.amazonaws.com')

# Configure the AWS environment
ENV = env.str('ENV', default=None)

print(f"ENV is {ENV}")

CONFIG = {'env': ENV, 'debug': False}

DEVELOP = env.bool('DEVELOP', default=False)

KEY = env.str('KEY', default=ENV)
rsa_keys = {}

# Provide this value if `id_token` is used for authentication (it contains 'aud' claim).
# `access_token` doesn't have it, in this case keep the COGNITO_AUDIENCE empty
COGNITO_AUDIENCE = None
COGNITO_POOL_URL = None  # will be set few lines of code later, if configuration provided

CONFIG['account'] = AWS_ACCOUNT
CONFIG['region'] = AWS_REGION
path = "/{0}/".format(ENV)

session = boto3.session.Session()
client = session.client(
    service_name='ssm',
    region_name=CONFIG['region'],
)
response = client.get_parameters_by_path(
    Path=path,
    Recursive=True,
)
for param in response['Parameters']:
    CONFIG[param['Name'].replace(path, '')] = param['Value']

while response.get('NextToken', None) is not None:
    response = client.get_parameters_by_path(
        Path=path,
        Recursive=True,
        NextToken=response['NextToken']
    )
    for param in response['Parameters']:
        CONFIG[param['Name'].replace(path, '')] = param['Value']

CONFIG['db_ssl_ca'] = 'rds-ca-2019-root.pem'

COGNITO_AWS_REGION = AWS_REGION
COGNITO_USER_POOL = CONFIG['COGNITO_USER_POOL']

# To avoid circular imports, we keep this logic here.
# On django init we download jwks public keys which are used to validate jwt tokens.
# For now there is no rotation of keys (seems like in Cognito decided not to implement it)
if COGNITO_AWS_REGION and COGNITO_USER_POOL:
    COGNITO_POOL_URL = 'https://cognito-idp.{}.amazonaws.com/{}'.format(COGNITO_AWS_REGION, COGNITO_USER_POOL)
    pool_jwks_url = COGNITO_POOL_URL + '/.well-known/jwks.json'
    jwks = json.loads(request.urlopen(pool_jwks_url).read())
    rsa_keys = {key['kid']: json.dumps(key) for key in jwks['keys']}

JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'devportal.utils.jwt.get_username_from_payload_handler',
    'JWT_DECODE_HANDLER': 'devportal.utils.jwt.cognito_jwt_decode_handler',
    'JWT_PUBLIC_KEY': rsa_keys,
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': COGNITO_AUDIENCE,
    'JWT_ISSUER': COGNITO_POOL_URL,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

SESSION_ENGINE = env.str('SESSION_ENGINE', default='django.contrib.sessions.backends.cached_db')
SESSION_CACHE_ALIAS = 'default'

EMAIL_HOST = CONFIG.get('SMTP_HOST')
EMAIL_PORT = 587

EMAIL_USE_TLS = bool(strtobool(CONFIG.get('EMAIL_USE_TLS', 'True')))
EMAIL_HOST_USER = CONFIG.get('SMTP_USER')
EMAIL_HOST_PASSWORD = CONFIG.get('SMTP_PASSWORD')
SERVER_EMAIL = CONFIG.get('DEFAULT_FROM_EMAIL', "")

# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.forms",
]
THIRD_PARTY_APPS = [
    'guardian',
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS = [
    "devportal.orchestrator",
    "devportal.users",
    "devportal.base",
    'jet.dashboard',
    'jet',
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "devportal.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    'django.contrib.auth.backends.RemoteUserBackend',
    "allauth.account.auth_backends.AuthenticationBackend",
    'guardian.backends.ObjectPermissionBackend',

]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "devportal.utils.middlewares.SetRemoteAddrFromForwardedFor",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.http.ConditionalGetMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "devportal.users.context_processors.allauth_settings",
            ],
        },
    }
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "SAMEORIGIN"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""DanielGagnon""", "daniel-gagnon@example.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
USE_ETAGS = True
# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = "username"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = "devportal.users.adapters.AccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
ACCOUNT_FORMS = {"signup": "devportal.users.forms.UserSignupForm"}
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = "devportal.users.adapters.SocialAccountAdapter"
# https://django-allauth.readthedocs.io/en/latest/forms.html
SOCIALACCOUNT_FORMS = {"signup": "devportal.users.forms.UserSocialSignupForm"}

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'smarterblinds.versioning.SmarterBlindsVersioning',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.AdminRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'devportal.utils.pagination.ResultSetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '12/minute',
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter', 'rest_framework.filters.OrderingFilter'
    ],
    'PAGE_SIZE': 1000,
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ORIGIN_ALLOW_ALL = bool(strtobool(CONFIG.get('CORS_ORIGIN_ALLOW_ALL', 'True')))
CACHE_MIDDLEWARE_KEY_PREFIX = env.str('CACHE_MIDDLEWARE_KEY_PREFIX', default=f'fpcache_{KEY}')
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django_ses.SESBackend')
SECURE_PROXY_SSL_HEADER = env.str('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=False)
USE_X_FORWARDED_PORT = env.bool('USE_X_FORWARDED_PORT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN', default=f".{CONFIG.get('DOMAIN_ROOT')}")
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=f"{CONFIG.get('DOMAIN_ROOT')}")
SECURE_BROWSER_XSS_FILTER = bool(strtobool(CONFIG.get('SECURE_BROWSER_XSS_FILTER', 'False')))
SECURE_CONTENT_TYPE_NOSNIFF = bool(strtobool(CONFIG.get('SECURE_CONTENT_TYPE_NOSNIFF', 'False')))
SECURE_HSTS_SECONDS = int(CONFIG.get('SECURE_HSTS_SECONDS', 3600))
SECURE_SSL_REDIRECT = bool(strtobool(CONFIG.get('SECURE_SSL_REDIRECT', 'False')))
CORS_ORIGIN_WHITELIST = CONFIG.get('CORS_ORIGIN_WHITELIST', "http://example.com").split(",")
DEFAULT_FROM_EMAIL = CONFIG.get('DEFAULT_FROM_EMAIL', "")


# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
SPECTACULAR_SETTINGS = {
    "TITLE": "devportal API",
    "DESCRIPTION": "Documentation of API endpoints of devportal",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}
# Your stuff...
# ------------------------------------------------------------------------------

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
LOGIN_REDIRECT_URL = '/#/overview'
LOGIN_URL = '/#/login'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/#/login'
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = True
