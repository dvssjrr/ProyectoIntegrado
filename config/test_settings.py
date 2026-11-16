"""
Configuración de Django para testing.
Usa SQLite en memoria para tests rápidos.
Hereda de settings.py las demás configuraciones.
"""
from .settings import *  # noqa: F401, F403

# Base de Datos: SQLite en memoria para tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }
}

# Deshabilitar migraciones en tests (speedup)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Logging deshabilitado en tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Credentials de prueba
SECRET_KEY = 'test-secret-key-for-testing-only'
DEBUG = True

# CORS más permisivo para tests
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
