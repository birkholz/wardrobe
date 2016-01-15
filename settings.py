from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
import os

DEBUG = False
REGISTER = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Brandon Birkholz', 'brandon@myoutfits.co'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['myoutfits.co',]
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = False
USE_L10N = True
USE_TZ = True


MEDIA_URL = '/media/'

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
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
    'south',
    'pytz',
    # 'social_auth',
    'timezone_field',
    'simplejson',
    'uuidfield',
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

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

try:
    from local_settings import *
except ImportError:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
