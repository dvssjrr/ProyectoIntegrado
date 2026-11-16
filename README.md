# 🏥 FARMASUR - Sistema de Gestión Farmacéutica

**Farmasur** es un sistema integral de gestión para farmacias que implementa mejores prácticas en arquitectura de software con una **estructura por capas** profesional y escalable.

---

## 📋 Tabla de Contenidos

1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
4. [Configuración](#configuración)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Uso](#uso)
7. [API REST](#api-rest)
8. [Testing](#testing)
9. [Documentación](#documentación)

---

## ✨ Características

### 🔐 Seguridad y Autenticación
- ✓ Autenticación por RUT (Rol Único Tributario) con validación de Módulo 11
- ✓ Control de Acceso basado en Roles (RBAC) con 4 niveles:
  - **Admin**: Control total del sistema
  - **Farmacéutico**: Gestión de recetas y medicamentos
  - **Técnico**: Soporte técnico
  - **Bodeguero**: Gestión de inventario
- ✓ Auditoría SHA-256 encadenada (inmutable)
- ✓ Protección CSRF en todos los endpoints

### 📦 Gestión de Inventario
- ✓ Algoritmo **FEFO** (First Expire First Out)
- ✓ Inventario dual: Vitrina + Bodega
- ✓ Control de stock en tiempo real
- ✓ Gestión de lotes y vencimientos
- ✓ Registro de mermas

### 💊 Gestión de Recetas
- ✓ Validación clínica de recetas
- ✓ Bloqueo automático después de 30 días
- ✓ Libro digital ISP (Institución de Salud Pública)
- ✓ Registro de unidosis asistencial

### 🛒 Punto de Venta (POS)
- ✓ Caja diaria con cuadratura
- ✓ Simulador de convenios Isapre
- ✓ Generación de comprobantes
- ✓ Reportes de ventas

### 🏗️ Arquitectura
- ✓ **Estructura por Capas**: Separación clara de responsabilidades
- ✓ **Django + DRF**: REST API moderna y robusta
- ✓ **PostgreSQL**: Base de datos relacional
- ✓ **Bootstrap**: Frontend responsivo

---

## 📦 Requisitos

### Sistema
- Python 3.9+
- PostgreSQL 12+
- pip

### Python
- Django 6.1+
- Django REST Framework 3.14+
- Python Decouple (variables de entorno)
- psycopg2-binary (driver PostgreSQL)

---

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/dvssjrr/ProyectoIntegrado.git
cd ProyectoIntegrado
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env.local
# Editar .env.local con tus credenciales
```

#### Variables Requeridas en `.env.local`:
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

### 5. Crear Base de Datos
```bash
# PostgreSQL CLI
createdb farmasur_db
createuser farmasur_user
```

O usar el script de setup:
```bash
# Windows
.\setup_postgres.ps1

# Linux/Mac
bash setup_postgres.sh
```

### 6. Crear Migraciones e Inicializar BD
```bash
python manage.py makemigrations farmasur
python manage.py migrate
```

### 7. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 8. Cargar Datos Iniciales (Opcional)
```bash
python manage.py seed_farmacia
```

### 9. Iniciar Servidor
```bash
python manage.py runserver
```

Acceder a:
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

---

## 🏗️ Estructura del Proyecto

### Arquitectura por Capas

```
farmacia_project/          ← Configuración centralizada
│
farmasur/                  ← Aplicación monolítica por capas
├── models/                ← CAPA 1: Modelos de datos
├── views/                 ← CAPA 2: Endpoints REST (ViewSets)
├── serializers/           ← CAPA 3: Validación de datos
├── services/              ← CAPA 4: Lógica de negocio
├── permissions/           ← CAPA 5: Control de acceso (RBAC)
├── validators/            ← CAPA 6: Validaciones reutilizables
├── urls/                  ← CAPA 7: Enrutamiento
├── forms/                 ← CAPA 8: Formularios Django
├── tests/                 ← CAPA 9: Pruebas automatizadas
├── migrations/            ← Migraciones de BD
├── static/                ← Archivos estáticos
├── apps.py                ← Config de la app
├── admin.py               ← Admin centralizado
└── __init__.py            ← Init del proyecto
│
farmasur_templates/        ← Frontend (HTML + Bootstrap)
```

### Módulos Funcionales

Cada capa está organizada por módulos:
- **usuarios/**: Autenticación, autorización, auditoria
- **inventario/**: Medicamentos, stock, lotes
- **recetas/**: Recetas médicas, libro ISP
- **ventas/**: Punto de venta, caja, reportes

### Ejemplo: Flujo de una Solicitud

```
GET /api/medicamentos/
  ↓
farmacia_project/urls.py → include('farmasur.urls')
  ↓
farmasur/urls/__init__.py → DefaultRouter → MedicamentoViewSet
  ↓
farmasur/views/inventario/views.py → ViewSet
  ↓
farmasur/permissions/inventario/permissions.py → Verificar RBAC
  ↓
farmasur/serializers/inventario/serializers.py → Validar datos
  ↓
farmasur/services/inventario/services.py → Lógica de negocio
  ↓
farmasur/models/inventario/models.py → Base de datos
  ↓
JSON Response
```

---

## 🔧 Configuración

### Variables de Entorno (`farmacia_project/settings.py`)

```python
# Base de Datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'farmasur',  ← Aplicación centralizada
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## 📡 Uso

### Admin Django

```bash
# Acceder a http://localhost:8000/admin/
# Usuario: (tu superusuario)
# Contraseña: (tu contraseña)
```

Dashboard con:
- Gestión de usuarios
- Catálogo de medicamentos
- Inventario
- Recetas
- Ventas y cajas

### API REST

#### Autenticación
```bash
# Obtener token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_rut","password":"tu_contrasena"}'

# Usar token en requests
curl -H "Authorization: Token TU_TOKEN_AQUI" \
  http://localhost:8000/api/medicamentos/
```

#### Endpoints Disponibles

```
# Usuarios
GET    /api/usuarios/              - Listar usuarios
POST   /api/usuarios/              - Crear usuario
GET    /api/usuarios/{id}/         - Detalle
PUT    /api/usuarios/{id}/         - Actualizar
DELETE /api/usuarios/{id}/         - Eliminar

# Medicamentos
GET    /api/medicamentos/          - Listar
POST   /api/medicamentos/          - Crear
GET    /api/medicamentos/{id}/     - Detalle
PUT    /api/medicamentos/{id}/     - Actualizar
DELETE /api/medicamentos/{id}/     - Eliminar

# Inventario
GET    /api/stock-vitrina/         - Stock en vitrina
GET    /api/stock-bodega/          - Stock en bodega
GET    /api/movimientos/           - Historial de movimientos

# Recetas
GET    /api/recetas/               - Listar recetas
POST   /api/recetas/               - Crear receta
GET    /api/libro-isp/             - Libro digital ISP

# Ventas
GET    /api/ventas/                - Listar ventas
POST   /api/ventas/                - Crear venta
GET    /api/cajas/                 - Gestión de cajas

# Auditoría
GET    /api/auditoria/             - Log de cambios
```

---

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test --settings=farmacia_project.test_settings

# Tests de un módulo específico
python manage.py test farmasur.tests.usuarios --settings=farmacia_project.test_settings

# Con coverage
coverage run --source='farmasur' manage.py test --settings=farmacia_project.test_settings
coverage report
coverage html
```

### Verificar Estructura
```bash
# Verificar que la estructura por capas esté correcta
python verify_structure_capas.py
```

---

## 📚 Documentación

### Archivos Principales

- **[ESTRUCTURA_CAPAS.md](./ESTRUCTURA_CAPAS.md)** - Documentación visual de la arquitectura
- **[CAMBIOS.txt](./CAMBIOS.txt)** - Historial de cambios previos
- **[README.md](./README.md)** - Este archivo

### Convenciones de Código

#### Modelos (`farmasur/models/{app}/models.py`)
```python
from django.db import models

class Usuario(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    rol = models.CharField(max_length=20, choices=ROLES)
    
    class Meta:
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.nombre
```

#### Serializers (`farmasur/serializers/{app}/serializers.py`)
```python
from rest_framework import serializers
from farmasur.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'rut', 'nombre', 'email', 'rol']
    
    def validate_rut(self, value):
        if not validar_rut(value):
            raise serializers.ValidationError("RUT inválido")
        return value
```

#### Views (`farmasur/views/{app}/views.py`)
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from farmasur.models import Usuario
from farmasur.serializers import UsuarioSerializer
from farmasur.permissions import IsAdmin

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
```

#### Services (`farmasur/services/{app}/services.py`)
```python
from django.db import transaction
from farmasur.models import Usuario

class UsuarioService:
    @staticmethod
    @transaction.atomic
    def crear_usuario(rut, nombre, email, rol):
        usuario = Usuario.objects.create(
            rut=rut,
            nombre=nombre,
            email=email,
            rol=rol
        )
        return usuario
```

---

## 🔐 Seguridad

### Mejores Prácticas Implementadas

✓ **Variables de Entorno**: Nunca commits de secrets  
✓ **CSRF Protection**: Habilitado en todos los formularios  
✓ **SQL Injection**: Prevenido mediante ORM de Django  
✓ **XSS Protection**: Templates escapados automáticamente  
✓ **RBAC**: Control de acceso basado en roles  
✓ **Auditoría**: Log SHA-256 encadenado de todos los cambios  
✓ **Autenticación**: Token de sesión + RUT validado  

### Secretos Sensibles (.env.local)
```
⚠️ NUNCA COMITEAR .env.local
⚠️ NUNCA HARDCODEAR SECRETOS EN EL CÓDIGO
✓ SIEMPRE usar .env.example como plantilla
✓ SIEMPRE usar variables de entorno
```

---

## 🚀 Despliegue en Producción

### Checklist Pre-Producción

- [ ] `DEBUG = False` en settings
- [ ] `SECRET_KEY` generada aleatoriamente
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] PostgreSQL configurado y respaldado
- [ ] SSL/HTTPS habilitado
- [ ] Variables de entorno configuradas
- [ ] Tests pasando (100%)
- [ ] Migraciones aplicadas
- [ ] Backups programados
- [ ] Monitoreo configurado

### Despliegue con Gunicorn
```bash
gunicorn farmacia_project.wsgi --bind 0.0.0.0:8000 --workers 4
```

### Despliegue con Docker
```bash
docker build -t farmasur .
docker run -p 8000:8000 --env-file .env.local farmasur
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Add nueva-funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](./LICENSE) para más detalles.

---

## 📞 Soporte

Para reportar bugs o solicitar features:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo

---

## 👥 Autores

- **Equipo Farmasur** - Desarrollo inicial
- **Copilot** - Restructuración a arquitectura por capas

---

## 🗂️ Historial de Versiones

### v2.0.0 - Estructura por Capas (Actual)
- Reorganización a arquitectura por capas
- Consolidación de apps en `farmasur/{capas}`
- Centralización de configuración en `farmacia_project`
- Admin centralizado
- URLs centralizadas con DefaultRouter
- Documentación visual

### v1.0.0 - Estructura Original
- Versión inicial con apps separadas
- Modelos, views, serializers en cada app
- Configuración en `config/`

---

**Última actualización**: 16/11/2026  
**Versión**: 2.0.0
