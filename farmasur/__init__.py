"""
Farmasur - Sistema de Gestión Farmacéutica

Estructura por capas:
  - models/: Entidades y relaciones de base de datos
  - views/: ViewSets REST de Django REST Framework
  - serializers/: Validación y transformación de datos
  - services/: Lógica de negocio y operaciones transaccionales
  - permissions/: Control de acceso basado en roles (RBAC)
  - validators/: Validaciones específicas de negocio
  - urls/: Enrutamiento centralizado
  - forms/: Formularios Django
  - static/: Archivos estáticos (CSS, JS, imágenes)
  - migrations/: Historial de cambios en la base de datos
  - tests/: Pruebas automatizadas
"""

default_app_config = 'farmasur.apps.FarmasurConfig'

__version__ = '1.0.0'
__author__ = 'Farmasur Development Team'
