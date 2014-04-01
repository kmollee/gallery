import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = TEMPLATE_DEBUG = True

INTERNAL_IPS = ('127.0.0.1', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'database.sqlite3')
    }
}

ADMINS = (
    ('Local Admin', 'root@localhost'),
)

MANAGERS = ADMINS

SECRET_KEY = 'PLEASE-OVERRIDE-IN-LOCAL-SETTINGS'

USE_TZ = True
TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False

ROOT_URLCONF = 'gallery.urls'

WSGI_APPLICATION = 'gallery.wsgi.application'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts:login'
LOGOUT_URL = 'accounts:logout'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'tmp', 'cache'),
    }
}

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'gallery', 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

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
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'gallery', 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'pipeline',
    'accounts',
    'photos',
    'stream',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.ExceptionLoggingMiddleware',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
STATIC_URL = '/static/'

PIPELINE_CSS = {
    'gallery': {
        'source_filenames': (
            'css/reset.css',
            'css/fonts.css',
            'css/base.css',
            'chosen-1.1.0/chosen.css'
        ),
        'output_filename': 'css/gallery.css',
    },
}

PIPELINE_JS = {
    'gallery': {
        'source_filenames': (
            'js/base.js',
            'chosen-1.1.0/chosen.jquery.js',
        ),
        'output_filename': 'js/gallery.js',
    }
}

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CSSMinCompressor'

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'

ALLOWED_EXTENSIONS = 'zip bmp raw jpg jpeg png gif tiff'.split()

AUTH_CODE_USER = 'auth-code-user'
AUTH_CODE_ADMIN = 'auth-code-admin'
AUTH_CODE_ADMIN_GROUP = 'Admin Group'

PHOTOS_PER_PAGE = 50

try:
    from .settings_local import *
except ImportError:
    pass
