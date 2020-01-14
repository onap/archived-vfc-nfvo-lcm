# Copyright 2016 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import platform

import lcm.pub.redisco

from lcm.pub.config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWD
from lcm.pub.config.config import DB_NAME, DB_IP, DB_USER, DB_PASSWD, DB_PORT
from lcm.pub.config import config as pub_config
from logging import config as log_config
from onaplogging import monkey
monkey.patch_all()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3o-wney!99y)^h3v)0$j16l9=fdjxcb+a8g+q3tfbahcnu2b0o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'lcm.pub.database',
    'lcm.swagger',
    # 'django_nose',
    'drf_yasg'
]
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login',
    'LOGOUT_URL': '/admin/logout',
    'DEFAULT_INFO': 'lcm.swagger.urls.swagger_info'
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lcm.middleware.LogContextMiddleware',
]

ROOT_URLCONF = 'lcm.urls'

WSGI_APPLICATION = 'lcm.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        # 'rest_framework.parsers.FileUploadParser',
    )
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'HOST': DB_IP,
        'PORT': DB_PORT,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWD,
    },
}

# DATABASES = {}
# DATABASES['default'] = {
#    'ENGINE': 'django.db.backends.sqlite3',
#    'NAME': 'D:/etsi-plug-test/db/nfvo',
# }

lcm.pub.redisco.connection_setup(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWD, db=0)
# CACHE_BACKEND = 'redis_cache.cache://%s@%s:%s' % (REDIS_PASSWD, REDIS_HOST, REDIS_PORT)

TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

pub_config.AAI_BASE_URL = "%s/aai/v11" % pub_config.MSB_BASE_URL
pub_config.SDC_BASE_URL = "%s/api" % pub_config.MSB_BASE_URL

if platform.system() == 'Windows' or 'test' in sys.argv:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s:[%(name)s]:[%(filename)s]-[%(lineno)d] [%(levelname)s]:%(message)s',
            },
        },
        'filters': {
        },
        'handlers': {
            'lcm_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/runtime_lcm.log'),
                'formatter': 'standard',
                'maxBytes': 1024 * 1024 * 50,
                'backupCount': 5,
            },
        },

        'loggers': {
            'lcm': {
                'handlers': ['lcm_handler'],
                'level': 'DEBUG',
                'propagate': False
            },
        }
    }
else:
    LOGGING_CONFIG = None
    # yaml configuration of logging
    LOGGING_FILE = os.path.join(BASE_DIR, 'lcm/log.yml')
    log_config.yamlConfig(filepath=LOGGING_FILE, watchDog=True)

if 'test' in sys.argv:
    pub_config.REG_TO_MSB_WHEN_START = False
    pub_config.DEPLOY_WORKFLOW_WHEN_START = False
    pub_config.REPORT_TO_AAI = False
    DATABASES = {}
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    REST_FRAMEWORK = {}

    if platform.system() == 'Linux':
        TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
        TEST_OUTPUT_VERBOSE = True
        TEST_OUTPUT_DESCRIPTIONS = True
        TEST_OUTPUT_DIR = 'test-reports'

    import mock
    from lcm.pub.utils import idutil
    idutil.get_auto_id = mock.Mock()
    idutil.get_auto_id.return_value = 1
