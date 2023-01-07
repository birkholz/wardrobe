import os

DEBUG = bool(os.environ.get('DJANGO_DEBUG', 0))
TEMPLATE_DEBUG = DEBUG

REGISTER = True

ADMINS = (
    ('Brandon Birkholz', 'brandon@myoutfits.co'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['myoutfits.co',]
if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1']


TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = False
USE_L10N = True
USE_TZ = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'wardrobe.tz_middleware.TimezoneMiddleware',
    'impersonate.middleware.ImpersonateMiddleware'
)

ROOT_URLCONF = 'wardrobe.urls'
WSGI_APPLICATION = 'wardrobe.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'pytz',
    # 'social_auth',
    'timezone_field',
    'simplejson',
    'wardrobe',
    'impersonate',
    'storages',
    # 'sorl.thumbnail'
)

LOGIN_URL = '/sign_in/'
LOGIN_REDIRECT_URL = '/outfits/'
LOGIN_ERROR_URL = '/sign_in/?error=true'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

try:
    from local_settings import *
except ImportError:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
S3_URL = 'http://%s.s3-website-us-east-1.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL + 'static/'
MEDIA_URL = S3_URL + 'media/'