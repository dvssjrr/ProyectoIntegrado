# 🚀 REFERENCIA RÁPIDA - FARMASUR v2.0.0

## Estructura por Capas

```
farmacia_project/   ← Configuración (Django settings, urls, wsgi, asgi)
farmasur/           ← Aplicación principal (11 capas organizadas)
  ├── models/       ← Entidades y relaciones
  ├── views/        ← Endpoints REST (ViewSets)
  ├── serializers/  ← Validación de datos
  ├── services/     ← Lógica de negocio
  ├── permissions/  ← Control de acceso (RBAC)
  ├── validators/   ← Validaciones reutilizables
  ├── urls/         ← Enrutamiento (DefaultRouter)
  ├── forms/        ← Formularios Django
  ├── tests/        ← Pruebas automatizadas
  ├── migrations/   ← Historial de BD
  └── static/       ← CSS, JS, imágenes
farmasur_templates/ ← Frontend (HTML + Bootstrap)
```

## Comandos Comunes

### Instalación y Setup
```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local

# Crear BD y aplicar migraciones
python manage.py makemigrations farmasur
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### Desarrollo
```bash
# Iniciar servidor
python manage.py runserver

# Ejecutar tests
python manage.py test --settings=farmacia_project.test_settings

# Verificar estructura
python verify_structure_capas.py

# Crear migraciones
python manage.py makemigrations farmasur

# Aplicar migraciones
python manage.py migrate

# Acceder a la app
# Admin: http://localhost:8000/admin/
# API:   http://localhost:8000/api/
```

## Importaciones Comunes

```python
# Modelos
from farmasur.models import Usuario, Medicamento, Receta, Venta

# ViewSets
from farmasur.views import UsuarioViewSet, MedicamentoViewSet

# Serializers
from farmasur.serializers import UsuarioSerializer, MedicamentoSerializer

# Services
from farmasur.services import UsuarioService, calcular_fefo

# Permissions
from farmasur.permissions import IsAdmin, CanEditInventario

# Validators
from farmasur.validators import validar_rut, validar_stock
```

## Estructura de Carpetas por Módulo

Cada módulo (usuarios, inventario, recetas, ventas) tiene la misma estructura:

```
farmasur/
├── models/usuarios/models.py
├── views/usuarios/views.py
├── serializers/usuarios/serializers.py
├── services/usuarios/services.py
├── permissions/usuarios/permissions.py
├── validators/usuarios/validators.py
├── urls/usuarios/urls.py
├── forms/usuarios/forms.py
└── tests/usuarios/test_usuarios.py
```

## Endpoints API

### Base URL
```
http://localhost:8000/api/
```

### Usuarios
- `GET    /usuarios/`             - Listar
- `POST   /usuarios/`             - Crear
- `GET    /usuarios/{id}/`        - Detalle
- `PUT    /usuarios/{id}/`        - Actualizar
- `DELETE /usuarios/{id}/`        - Eliminar

### Medicamentos
- `GET    /medicamentos/`         - Listar
- `POST   /medicamentos/`         - Crear
- `GET    /medicamentos/{id}/`    - Detalle

### Inventario
- `GET    /stock-vitrina/`        - Stock en vitrina
- `GET    /stock-bodega/`         - Stock en bodega
- `GET    /movimientos/`          - Historial

### Recetas
- `GET    /recetas/`              - Listar
- `POST   /recetas/`              - Crear
- `GET    /libro-isp/`            - Libro digital ISP

### Ventas
- `GET    /ventas/`               - Listar
- `POST   /ventas/`               - Crear
- `GET    /cajas/`                - Gestión de cajas

### Auditoría
- `GET    /auditoria/`            - Log de cambios

## Autenticación

```bash
# 1. Obtener token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_rut","password":"tu_contrasena"}'

# 2. Usar token en requests
curl -H "Authorization: Token TU_TOKEN_AQUI" \
  http://localhost:8000/api/medicamentos/
```

## Creación de Modelos

### 1. Crear modelo en `farmasur/models/{app}/models.py`
```python
from django.db import models

class MiModelo(models.Model):
    nombre = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = 'MisModelos'
    
    def __str__(self):
        return self.nombre
```

### 2. Crear serializer en `farmasur/serializers/{app}/serializers.py`
```python
from rest_framework import serializers
from farmasur.models import MiModelo

class MiModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiModelo
        fields = ['id', 'nombre']
```

### 3. Crear ViewSet en `farmasur/views/{app}/views.py`
```python
from rest_framework import viewsets
from farmasur.models import MiModelo
from farmasur.serializers import MiModeloSerializer

class MiModeloViewSet(viewsets.ModelViewSet):
    queryset = MiModelo.objects.all()
    serializer_class = MiModeloSerializer
```

### 4. Registrar en `farmasur/urls/__init__.py`
```python
from rest_framework.routers import DefaultRouter
from farmasur.views.mimodulo.views import MiModeloViewSet

router = DefaultRouter()
router.register(r'mimodelo', MiModeloViewSet)
```

### 5. Registrar en admin `farmasur/admin.py`
```python
from django.contrib import admin
from farmasur.models import MiModelo

@admin.register(MiModelo)
class MiModeloAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
```

## Creación de Services (Lógica de Negocio)

```python
# farmasur/services/usuarios/services.py
from django.db import transaction
from farmasur.models import Usuario

class UsuarioService:
    @staticmethod
    @transaction.atomic
    def crear_usuario(rut, nombre, email):
        usuario = Usuario.objects.create(
            rut=rut,
            nombre=nombre,
            email=email
        )
        return usuario
```

## Testing

```bash
# Ejecutar todos los tests
python manage.py test --settings=farmacia_project.test_settings

# Ejecutar tests de un módulo
python manage.py test farmasur.tests.usuarios --settings=farmacia_project.test_settings

# Ejecutar con coverage
coverage run --source='farmasur' manage.py test --settings=farmacia_project.test_settings
coverage report
```

## Convenciones

### Nombres de Variables
- Modelos: Singular, PascalCase (`Usuario`, `Medicamento`)
- Tablas: Plural, snake_case (automático en Django)
- Views: Singular + "ViewSet" (`UsuarioViewSet`)
- Serializers: Singular + "Serializer" (`UsuarioSerializer`)
- Services: Singular + "Service" (`UsuarioService`)

### Archivos
- Models: `models.py`
- Views: `views.py`
- Serializers: `serializers.py`
- Services: `services.py`
- Permissions: `permissions.py`
- Validators: `validators.py`
- URLs: `urls.py`
- Forms: `forms.py`
- Tests: `test_*.py`

## Variables de Entorno (.env.local)

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=farmasur_db
DB_USER=farmasur_user
DB_PASSWORD=tu-contrasena-segura
DB_HOST=localhost
DB_PORT=5432

# Opcionales
TIME_ZONE=America/Santiago
LANGUAGE_CODE=es-cl
```

## Despliegue

### Producción con Gunicorn
```bash
gunicorn farmacia_project.wsgi --bind 0.0.0.0:8000 --workers 4
```

### Checklist Pre-Producción
- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` generada aleatoriamente
- [ ] `ALLOWED_HOSTS` configurado
- [ ] PostgreSQL setup y respaldado
- [ ] SSL/HTTPS habilitado
- [ ] Variables de entorno configuradas
- [ ] Tests pasando (100%)
- [ ] Migraciones aplicadas
- [ ] Backups programados

## Recursos

- **Documentación Completa**: [README.md](./README.md)
- **Estructura Visual**: [ESTRUCTURA_CAPAS.md](./ESTRUCTURA_CAPAS.md)
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **PostgreSQL**: https://www.postgresql.org/docs/

## Contacto y Soporte

Para reportar bugs o solicitar features:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo

---

**Versión**: 2.0.0  
**Última actualización**: 16/11/2026  
**Estado**: Producción lista ✅
