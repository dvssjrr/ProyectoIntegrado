"""
Configuración de la aplicación Farmasur.
"""
from django.apps import AppConfig


class FarmasurConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'farmasur'
    verbose_name = 'Sistema de Gestión Farmacéutica Farmasur'

    def ready(self):
        """
        Importar señales y realizar inicializaciones cuando la app esté lista.
        """
        from farmasur import signals  # noqa: F401
