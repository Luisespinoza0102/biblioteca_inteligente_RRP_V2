import os
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables desde el archivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD
# Si no encuentra la variable en el .env, usa un valor por defecto (útil para evitar errores)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# En Docker es vital que ALLOWED_HOSTS incluya '0.0.0.0' o '*' en desarrollo
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Mis Apps
    'core',
    'catalog',
    'loans',
    'recommendation',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'loans.context_processors.contadores_biblioteca',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# BASE DE DATOS (Configurada para Docker y Local)
# IMPORTANTE: En Docker, el HOST debe ser el nombre del servicio en docker-compose o 'host.docker.internal'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'ramon_ruiz_polanco_v2'),
        'USER': os.getenv('DB_USER', 'Espinoza'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'luisjose123'),
        'HOST': os.getenv('DB_HOST', 'db'), # 'db' es el nombre estándar en Docker
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# VALIDACIÓN DE PASSWORDS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas' # Ajustado a tu zona horaria
USE_I18N = True
USE_TZ = True

# ARCHIVOS ESTÁTICOS Y MEDIA
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' # Necesario para producción/Docker

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# LOGIN / LOGOUT
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dispatch_dashboard'
LOGOUT_REDIRECT_URL = 'login'

# EMAIL (Variables en .env para no exponer contraseñas de aplicación)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER', 'bibliotecarrpv2.0@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS', 'aleh vifi fyxu jgyk')
DEFAULT_FROM_EMAIL = f"Biblioteca RRP <{EMAIL_HOST_USER}>"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'