# -*- coding: utf-8 -*-
import os.path
import sys

#########################
### Universal Paths
#########################

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DJANGO_ROOT = os.path.abspath(os.path.dirname(PROJECT_ROOT))
LOG_ROOT = os.path.join(DJANGO_ROOT, 'logs')

BASE_URL = 'http://localhost:8000' #No / at end

sys.path.append(PROJECT_ROOT)

########################
### Debug Settings
########################

# Never deploy a site into production with DEBUG turned on!
DEBUG = True
# Display a detailed report for any TemplateSyntaxError.
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ['127.0.0.1']

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'lightshowmaker.wsgi.application'

########################
### Database
########################

# In order to have transactions, the DB engine must either be PostgreSQL or MySQL.
# In the last case, the storage engine must be InnoDB, not MyISAM.
# Transaction Middleware is also recommended.
# To ignore transactions locally, override these values in the local settings.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # 'django.db.backends.' plus 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DJANGO_ROOT, 'lightshowmaker.db'),          # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


########################
### Static & Media
########################

# Absolute path to the directory where collectstatic will collect static files 
STATIC_ROOT = os.path.join(DJANGO_ROOT, 'static')
# Locations collectstatic will traverse to find static files
STATICFILES_DIRS = os.path.join(PROJECT_ROOT, 'static'),
# URL to use when referring to static files located in STATIC_ROOT (must end in a slash)
STATIC_URL = '/static/'

# Absolute path to the directory that holds dynamic media, like file uploads.
MEDIA_ROOT = os.path.join(DJANGO_ROOT, 'media')
# URL that handles the media served from MEDIA_ROOT (must end in a slash)
MEDIA_URL = '/media/'

########################
### Logging
########################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple':  { 'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s' },
        'verbose': { 'format': '%(asctime)s [%(levelname)s] {PID %(process)d:%(thread)d} %(name)s: %(message)s' },
    },
    'handlers': {
        'console':     { 'level': 'DEBUG', 'class': 'logging.StreamHandler',  },
        'logfile': { 'level': 'DEBUG', 'class': 'logging.FileHandler', 'formatter': 'verbose', 'filename': os.path.join(LOG_ROOT, 'django.log') },
        'logfile_sql': { 'level': 'DEBUG', 'class': 'logging.FileHandler', 'formatter': 'verbose', 'filename': os.path.join(LOG_ROOT, 'sql.log') },
        'mail_admins': { 'level': 'ERROR', 'class': 'django.utils.log.AdminEmailHandler', 'formatter': 'verbose', 'include_html': True },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse',
         }
     },
    'loggers': {
        '': { 
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level' : 'DEBUG',
            'filters': ['require_debug_false'],
            'propagate': True,
        },
        'django.db.backends': { 
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level' : 'INFO',
            'propagate': False,
        },
        'django.request': { 
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'DEBUG',  
            'propagate': False 
        },
        'werkzeug': { 
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'DEBUG',  
            'propagate': False 
        },
    }
}

#####################
### Apps and Plugins
#####################

# The full Python import path to the root URLconf
ROOT_URLCONF = 'lightshowmaker.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    
    'django_extensions',
    'south',
    
    'lightshowmaker'
)

# List of locations of the template source files, in search order
TEMPLATE_DIRS = os.path.join(PROJECT_ROOT, 'templates'),

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages'
)


# A tuple of middleware classes to use
MIDDLEWARE_CLASSES = (    
    #'util.http_response.HttpResponseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
   # 'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# List of classes that know how to find static files
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#######################
### Caching & Sessions 
#######################
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db' # Write through cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#########################################
### Internationalization and Performance
#########################################

# The time zone for this installation
TIME_ZONE = 'America/Los_Angeles'
# Output the 'Etag' header. This saves bandwidth but slows down performance. And breaks the admin.
USE_ETAGS = False
# Display numbers and dates using the format of the current locale
USE_L10N = False
# Enable Django's internationalization system - slows down performance
USE_I18N = False
# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

##############################################
### Miscellaneous You Shouldn't Have To Touch
##############################################

# Maximum size (in bytes) before an upload gets streamed to the file system.
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
# List of locations of the fixture data files, in search order
FIXTURE_DIRS = ()
# Seed for secret-key hashing algorithms.  Make this unique, and don't share it with anybody.
SECRET_KEY = 'qb29de+5ph*os%c^0nvi4hi^4^m^han2t7a@g$*+a48zpzpe)v'
# The ID of the current site in the django_site database table
SITE_ID = 1


