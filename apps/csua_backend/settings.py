"""
Django settings for csua_backend project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from pathlib import Path
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType, LDAPGroupQuery

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DJANGO_DEBUG", False))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = str(Path(__file__).parent.parent.parent)

PROJECT_HOME = BASE_DIR

FIXTURE_DIRS = [os.path.join(BASE_DIR, "fixtures")]

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(PROJECT_HOME, "csua.sqlite3"),
        }
    }
    DATABASE_ROUTERS = ["ldapdb.router.Router"]
else:
    with open("/etc/secrets/db_pass.secret") as f:
        DB_PASS = f.read().strip()

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "csua_backend",
            # The following settings are not used with sqlite3:
            "USER": "pnunez",
            "PASSWORD": DB_PASS,
            "HOST": "",  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            "PORT": "",  # Set to empty string for default.
            "TEST": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(PROJECT_HOME, "csua.sqlite3"),
                "USER": "",
                "PASSWORD": "",
            },
        }
    }
    DATABASE_ROUTERS = ["ldapdb.router.Router"]

ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, "ldap_csua_berkeley_edu_interm.cer")
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

if DEBUG:
    # Read-only LDAP connection for now (no auth)
    DATABASES["ldap"] = {
        "ENGINE": "ldapdb.backends.ldap",
        "NAME": "ldaps://tap.csua.berkeley.edu/",
        "CONNECTION_OPTIONS": {ldap.OPT_X_TLS_DEMAND: True},
    }
else:
    DATABASES["ldap"] = {
        "ENGINE": "ldapdb.backends.ldap",
        "NAME": "ldaps://tap.csua.berkeley.edu/",
        "CONNECTION_OPTIONS": {ldap.OPT_X_TLS_DEMAND: True},
        # TODO: populate this with some ldap admin dummy user
        # "USER": "uid=,ou=People,dc=csua,dc=berkeley,dc=edu",
        # "PASSWORD": "",
    }

    # Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "www.csua.berkeley.edu",
    "csua.berkeley.edu",
    "legacy.csua.berkeley.edu",
    "dev.csua.berkeley.edu",
]
if DEBUG:
    ALLOWED_HOSTS.extend(["*"])

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "America/Los_Angeles"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_HOME, "media_root/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_HOME, "static_root/")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

# Security
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_Forwarded_Proto", "https")
X_FRAME_OPTIONS = "SAMEORIGIN"

# SECURITY WARNING: keep the secret key used in production secret!
# Make this unique, and don't share it with anybody.
if DEBUG:
    SECRET_KEY = "CSUA)@3zekni&mwis6s031xsru2v&h(y=l89oa4@^&i#lxfoa9p9"
else:
    with open("/etc/secrets/secret_key.secret") as f:
        SECRET_KEY = f.read().strip()


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_LDAP_SERVER_URI = "ldaps://ldap.csua.berkeley.edu"
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_X_TLS_CACERTFILE: "ldap_csua_berkeley_edu_interm.cer",
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_ALLOW,
}
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "ou=People,dc=csua,dc=berkeley,dc=edu", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=Group,dc=csua,dc=berkeley,dc=edu",
    ldap.SCOPE_SUBTREE,
    "(objectClass=posixGroup)",
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

AUTH_LDAP_USER_ATTR_MAP = {"first_name": "gecos", "last_name": "gecos", "mail": "gecos"}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": (
        LDAPGroupQuery("cn=root,ou=Group,dc=csua,dc=berkeley,dc=edu")
        | LDAPGroupQuery("cn=excomm,ou=Group,dc=csua,dc=berkeley,dc=edu")
    ),
    "is_superuser": LDAPGroupQuery("cn=root,ou=Group,dc=csua,dc=berkeley,dc=edu"),
    "is_active": LDAPGroupQuery("cn=root,ou=Group,dc=csua,dc=berkeley,dc=edu"),
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
AUTH_LDAP_MIRROR_GROUPS = True
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
            os.path.join(PROJECT_HOME, "templates")
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "apps.csua_backend.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "apps.csua_backend.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    ## Our apps
    "apps.main_page",
    "apps.newuser",
    "apps.db_data",
    "apps.tracker",
    "apps.ldap_data",
    "apps.philbot",
    "apps.outreach",
    ## Third-party
    "ldapdb",
    "markdown_deux",
    "sorl.thumbnail",
]

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"


ADMINS = (("Robert Quitt", "robertq@csua.berkeley.edu"),)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = "django@csua.berkeley.edu"

SERVER_EMAIL = "django-errors@csua.berkeley.edu"

EMAIL_HOST = "mail.csua.berkeley.edu"

EMAIL_PORT = 25

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "server.log"),
        },
        "errorfile": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "error.log"),
        },
    },
    "loggers": {
        "django.request": {"handlers": ["file"], "level": "ERROR", "propagate": True},
        "django.security.csrf": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

SLACK_CLIENT_ID = "3311748471.437459179046"
try:
    with open("/etc/secrets/slack.txt") as f:
        SLACK_CLIENT_SECRET = f.readline().strip()
        SLACK_BOT_USER_TOKEN = f.readline().strip()
        SLACK_SIGNING_SECRET = f.readline().strip()
        SLACK_VERIFICATION_TOKEN = f.readline().strip()
except FileNotFoundError:
    SLACK_CLIENT_SECRET = ""
    SLACK_BOT_USER_TOKEN = ""
    SLACK_SIGNING_SECRET = ""
    SLACK_VERIFICATION_TOKEN = ""

## LDAP CONFIG ##
DATABASE_ROUTERS = ["ldapdb.router.Router"]

ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, "ldap_csua_berkeley_edu_interm.cer")
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

DATABASES["ldap"] = {
    "ENGINE": "ldapdb.backends.ldap",
    "NAME": "ldaps://tap.csua.berkeley.edu/",
    "CONNECTION_OPTIONS": {ldap.OPT_X_TLS_DEMAND: True},
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_LDAP_SERVER_URI = "ldaps://ldap.csua.berkeley.edu"

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_X_TLS_CACERTFILE: "ldap_csua_berkeley_edu_interm.cer",
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_ALLOW,
}

AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "ou=People,dc=csua,dc=berkeley,dc=edu", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=Group,dc=csua,dc=berkeley,dc=edu",
    ldap.SCOPE_SUBTREE,
    "(objectClass=posixGroup)",
)

AUTH_LDAP_GROUP_TYPE = PosixGroupType()

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "gecos.split(',')[0].split(' ')[0]",
    "last_name": "gecos.split(',')[0].split(' ')[1]",
    "mail": "gecos.split(',')[1]",
}

IS_ROOT = LDAPGroupQuery("cn=root,ou=Group,dc=csua,dc=berkeley,dc=edu")
IS_PB = LDAPGroupQuery("cn=excomm,ou=Group,dc=csua,dc=berkeley,dc=edu")
IS_OFFICER = LDAPGroupQuery("cn=officers,ou=Group,dc=csua,dc=berkeley,dc=edu")

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": IS_ROOT | IS_PB,
    "is_superuser": IS_ROOT,
    "is_active": IS_ROOT | IS_PB | IS_OFFICER,
}

AUTH_LDAP_ALWAYS_UPDATE_USER = False

AUTH_LDAP_MIRROR_GROUPS = True

AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

THUMBNAIL_DEBUG = DEBUG
