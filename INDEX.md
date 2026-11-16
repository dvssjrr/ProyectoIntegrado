# 📚 Índice de Documentación - FARMASUR v2.0.0

## Archivos de Documentación

### 🎯 Para Empezar (Lee primero)
1. **[README.md](./README.md)** - Documentación completa del proyecto
   - Descripción general y características
   - Requisitos e instalación
   - Estructura del proyecto
   - Configuración y uso
   - Testing y deployment

2. **[QUICKSTART.md](./QUICKSTART.md)** - Referencia rápida
   - Comandos comunes
   - Importaciones frecuentes
   - Endpoints API
   - Convenciones de código
   - Checklist de desarrollo

### 🏗️ Arquitectura y Estructura
3. **[ESTRUCTURA_CAPAS.md](./ESTRUCTURA_CAPAS.md)** - Guía visual de la arquitectura
   - Diagrama de carpetas
   - Responsabilidades por capa
   - Flujo de solicitudes HTTP
   - Importaciones centralizadas
   - Cambios desde la estructura anterior

### 📋 Referencia de Cambios
4. **[CAMBIOS.txt](./CAMBIOS.txt)** - Historial de cambios previos
   - Versión 1.0.0 (estructura anterior)
   - Detalles de restructuración

---

## Guía de Lectura por Rol

### Para Nuevos Desarrolladores
1. Leer: README.md (sección Estructura)
2. Leer: ESTRUCTURA_CAPAS.md (completo)
3. Leer: QUICKSTART.md (secciones: Comandos, Importaciones, Creación de Modelos)
4. Ejecutar: `python verify_structure_capas.py`
5. Explorar: Navegar carpetas en VS Code

### Para Líderes Técnicos
1. Leer: README.md (completo)
2. Leer: ESTRUCTURA_CAPAS.md (completo)
3. Revisar: Convenciones en QUICKSTART.md
4. Verificar: Testing en README.md
5. Planificar: Despliegue en README.md

### Para DevOps/Infraestructura
1. Leer: README.md (secciones: Requisitos, Configuración, Despliegue)
2. Revisar: Variables de entorno en QUICKSTART.md
3. Implementar: Checklist pre-producción
4. Configurar: PostgreSQL, SSL, Backups

### Para QA/Testers
1. Leer: README.md (sección Testing)
2. Estudiar: Endpoints en QUICKSTART.md
3. Revisar: Convenciones en QUICKSTART.md
4. Ejecutar: Tests locales
5. Validar: Verificador de estructura

---

## Estructura de Carpetas

```
📁 D:\progra\ProyectoIntegrado
├── 📄 README.md ...................... Documentación principal
├── 📄 QUICKSTART.md .................. Referencia rápida
├── 📄 ESTRUCTURA_CAPAS.md ............ Guía de arquitectura
├── 📄 CAMBIOS.txt .................... Historial de cambios
├── 📄 INDEX.md ....................... Este archivo
│
├── 📁 farmacia_project/         Configuración centralizada
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── test_settings.py
│
├── 📁 farmasur/              Aplicación por capas
│   ├── models/
│   ├── views/
│   ├── serializers/
│   ├── services/
│   ├── permissions/
│   ├── validators/
│   ├── urls/
│   ├── forms/
│   ├── tests/
│   ├── migrations/
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   └── __init__.py
│
├── 📁 farmasur_templates/        Frontend (HTML + Bootstrap)
│
├── 📄 manage.py                  Django CLI
├── 📄 requirements.txt           Dependencias Python
├── 📄 .env.example               Plantilla de variables
├── 📄 .gitignore                 Archivos ignorados
└── 📄 verify_structure_capas.py   Verificador
```

---

## Comandos Rápidos

```bash
# Instalación
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configuración
cp .env.example .env.local
# Editar .env.local

# Base de datos
python manage.py makemigrations farmasur
python manage.py migrate

# Desarrollo
python manage.py runserver

# Testing
python manage.py test --settings=farmacia_project.test_settings

# Verificación
python verify_structure_capas.py
```

---

## Capas y Responsabilidades

| Capa | Ubicación | Responsabilidad | Ejemplos |
|------|-----------|-----------------|----------|
| **Models** | `farmasur/models/` | Entidades y relaciones | `Usuario`, `Medicamento` |
| **Views** | `farmasur/views/` | Endpoints REST (ViewSets) | `UsuarioViewSet` |
| **Serializers** | `farmasur/serializers/` | Validación de datos | Validar RUT, email |
| **Services** | `farmasur/services/` | Lógica de negocio | FEFO, cálculos Isapre |
| **Permissions** | `farmasur/permissions/` | Control de acceso (RBAC) | IsAdmin, CanEdit |
| **Validators** | `farmasur/validators/` | Validaciones reutilizables | validar_rut() |
| **URLs** | `farmasur/urls/` | Enrutamiento (DefaultRouter) | Rutas automáticas |
| **Forms** | `farmasur/forms/` | Formularios Django | Validación HTML |
| **Tests** | `farmasur/tests/` | Pruebas automatizadas | test_usuarios.py |
| **Migrations** | `farmasur/migrations/` | Historial de BD | 0001_initial.py |
| **Static** | `farmasur/static/` | Archivos estáticos | CSS, JS, imágenes |

---

## Módulos Funcionales

Cada módulo tiene la misma estructura:

```
farmasur/
├── models/{app}/models.py
├── views/{app}/views.py
├── serializers/{app}/serializers.py
├── services/{app}/services.py
├── permissions/{app}/permissions.py
├── validators/{app}/validators.py
├── urls/{app}/urls.py
├── forms/{app}/forms.py
└── tests/{app}/test_{app}.py
```

### Módulos disponibles
- **usuarios**: Autenticación, autorización, auditoría
- **inventario**: Medicamentos, stock, lotes
- **recetas**: Recetas médicas, libro ISP
- **ventas**: POS, caja, reportes

---

## Flujo de una Solicitud

```
REQUEST: GET /api/medicamentos/
  ↓
farmacia_project/urls.py
  ↓ include('farmasur.urls')
  ↓
farmasur/urls/__init__.py (DefaultRouter)
  ↓
farmasur/views/inventario/views.py (ViewSet)
  ↓
farmasur/permissions/inventario/permissions.py (Verificar RBAC)
  ↓
farmasur/serializers/inventario/serializers.py (Validar)
  ↓
farmasur/services/inventario/services.py (Lógica)
  ↓
farmasur/models/inventario/models.py (Base de datos)
  ↓
RESPONSE: JSON con medicamentos
```

---

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

---

## Endpoints API

Base URL: `http://localhost:8000/api/`

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

---

## Convenciones

### Nombres
- Modelos: Singular, PascalCase (`Usuario`)
- Tablas: Plural, snake_case (automático)
- ViewSets: Singular + "ViewSet" (`UsuarioViewSet`)
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

---

## Variables de Entorno (.env.local)

```env
# Django
SECRET_KEY=tu-clave-secreta
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=farmasur_db
DB_USER=farmasur_user
DB_PASSWORD=tu-contrasena
DB_HOST=localhost
DB_PORT=5432

# Opcionales
TIME_ZONE=America/Santiago
LANGUAGE_CODE=es-cl
```

---

## Checklist de Desarrollo

### Antes de Programar
- [ ] Leer la documentación relevante
- [ ] Verificar la estructura existe
- [ ] Entender el flujo de la feature

### Mientras Programas
- [ ] Seguir las convenciones
- [ ] Escribir código limpio
- [ ] Agregar docstrings
- [ ] Incluir tests

### Antes de Commit
- [ ] Pasar todos los tests
- [ ] Verificar la estructura
- [ ] Revisar el código
- [ ] Escribir mensaje claro

### Antes de Producción
- [ ] DEBUG = False
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL setup
- [ ] SSL/HTTPS habilitado
- [ ] Backups programados

---

## Recursos Externos

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [REST API Best Practices](https://restfulapi.net/)

---

## Contacto y Soporte

Para reportar bugs o solicitar features:
- Abrir un issue en GitHub
- Contactar al equipo de desarrollo

---

**Versión**: 2.0.0  
**Última actualización**: 16/11/2026  
**Autor**: Equipo Farmasur + Copilot  
**Estado**: Producción lista ✅
