# -*- coding: utf-8 -*-
# Django settings for sandbox project.

import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Guillaume Pellerin', 'yomguy@parisson.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'telemeta_sandbox',                      # Or path to database file if using sqlite3.
        'USER': '********',                      # Not used with sqlite3.
        'PASSWORD': '********',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'fr_FR'
LANGUAGES = [ ('fr', 'French'),
	      ('en', 'English'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://localhost/django/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a8l7%06wr2k+3=%#*#@#rvop2mmzko)44%7k(zx%lls^ihm9^5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'sandbox.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'telemeta',
    'jsonrpc',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)

TELEMETA_ORGANIZATION = 'Parisson'
TELEMETA_SUBJECTS = ('test', 'telemeta', 'sandbox')
TELEMETA_GMAP_KEY = '***************************************************************************'
TELEMETA_DOWNLOAD_ENABLED = True
TELEMETA_STREAMING_FORMATS = ('mp3', 'ogg')
TELEMETA_PUBLIC_ACCESS_PERIOD = 51
AUTH_PROFILE_MODULE = 'telemeta.userprofile'

TELEMETA_OAI_REPOSITORY_NAME = "Telemeta TEST sandbox"

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
EMAIL_HOST = 'smtp.free.fr'
DEFAULT_FROM_EMAIL = 'webmaster@parisson.com'

TELEMETA_CACHE_DIR = MEDIA_ROOT + 'cache'
TELEMETA_EXPORT_CACHE_DIR = TELEMETA_CACHE_DIR + "/export"
TELEMETA_DATA_CACHE_DIR = TELEMETA_CACHE_DIR + "/data"
CACHE_BACKEND = "file://" + TELEMETA_CACHE_DIR + "/data"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

