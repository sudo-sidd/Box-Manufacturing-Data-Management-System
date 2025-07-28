# Example Django settings override for Docker
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'boxmfg'),
        'USER': os.environ.get('DJANGO_DB_USER', 'boxuser'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'boxpass'),
        'HOST': os.environ.get('DJANGO_DB_HOST', 'db'),
        'PORT': 5432,
    }
}
