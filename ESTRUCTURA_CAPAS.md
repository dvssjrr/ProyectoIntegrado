# 📊 Estructura de Capas - FARMASUR

## 🏗️ Organización General

```
ProyectoIntegrado/
│
├── farmacia_project/          ← Configuración centralizada (Django settings, urls, wsgi, asgi)
│   ├── __init__.py
│   ├── asgi.py               ← ASGI para Uvicorn/Daphne
│   ├── settings.py           ← Configuración principal
│   ├── test_settings.py      ← Configuración para testing (SQLite)
│   ├── urls.py               ← Rutas principales (incluye farmasur.urls)
│   └── wsgi.py               ← WSGI para Gunicorn
│
├── farmasur/                  ← Aplicación monolítica por capas
│   ├── __init__.py
│   ├── apps.py               ← Config de la app Django
│   ├── admin.py              ← Admin centralizado (todos los modelos)
│   │
│   ├── models/                ← CAPA 1: Modelos de datos
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── models.py
│   │
│   ├── views/                 ← CAPA 2: Endpoints REST (ViewSets)
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── views.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── views.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── views.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── views.py
│   │
│   ├── serializers/           ← CAPA 3: Validación y transformación de datos
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── serializers.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── serializers.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── serializers.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── serializers.py
│   │
│   ├── services/              ← CAPA 4: Lógica de negocio
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── services.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── services.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── services.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── services.py
│   │
│   ├── permissions/           ← CAPA 5: Control de acceso (RBAC)
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── permissions.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── permissions.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── permissions.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── permissions.py
│   │
│   ├── validators/            ← CAPA 6: Validaciones reutilizables
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── validators.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── validators.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── validators.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── validators.py
│   │
│   ├── urls/                  ← CAPA 7: Enrutamiento centralizado
│   │   ├── __init__.py        ← Rutas principales (DefaultRouter)
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── urls.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── urls.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── urls.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── urls.py
│   │
│   ├── forms/                 ← CAPA 8: Formularios Django
│   │   ├── __init__.py        ← Importador centralizado
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── forms.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── forms.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── forms.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── forms.py
│   │
│   ├── tests/                 ← CAPA 9: Pruebas automatizadas
│   │   ├── __init__.py
│   │   ├── usuarios/
│   │   │   ├── __init__.py
│   │   │   └── test_usuarios.py
│   │   ├── inventario/
│   │   │   ├── __init__.py
│   │   │   └── test_inventario.py
│   │   ├── recetas/
│   │   │   ├── __init__.py
│   │   │   └── test_recetas.py
│   │   └── ventas/
│   │       ├── __init__.py
│   │       └── test_ventas.py
│   │
│   ├── migrations/            ← Migraciones de base de datos
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── ...
│   │
│   └── static/                ← Archivos estáticos (CSS, JS, imágenes)
│       └── farmasur/
│           ├── css/
│           ├── js/
│           └── img/
│
├── farmasur_templates/        ← Frontend con Bootstrap en HTML
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── usuarios/
│   │   ├── lista.html
│   │   ├── crear.html
│   │   └── editar.html
│   ├── inventario/
│   │   ├── lista.html
│   │   ├── crear.html
│   │   └── detalle.html
│   ├── recetas/
│   │   ├── lista.html
│   │   └── detalle.html
│   └── ventas/
│       ├── punto_venta.html
│       └── reportes.html
│
├── manage.py                  ← Django management script
├── requirements.txt           ← Dependencias Python
├── README.md                  ← Documentación del proyecto
├── .gitignore                 ← Archivos ignorados por git
├── .env.local                 ← Variables de entorno (NO VERSIONADO)
└── .env.example               ← Plantilla de variables de entorno
```

## 🎯 Responsabilidades por Capa

| Capa | Ubicación | Responsabilidad | Ejemplo |
|------|-----------|-----------------|---------|
| **1. Models** | `farmasur/models/{app}/` | Entidades y relaciones de BD | `Usuario`, `Medicamento`, `Receta` |
| **2. Views** | `farmasur/views/{app}/` | Endpoints REST con ViewSets | `UsuarioViewSet`, `MedicamentoViewSet` |
| **3. Serializers** | `farmasur/serializers/{app}/` | Validación y transformación de datos | Validar RUT, formato de email |
| **4. Services** | `farmasur/services/{app}/` | Lógica de negocio reutilizable | FEFO, cálculo de convenios Isapre |
| **5. Permissions** | `farmasur/permissions/{app}/` | Control RBAC por rol | Admin, Farmacéutico, Técnico, Bodeguero |
| **6. Validators** | `farmasur/validators/{app}/` | Validaciones específicas de negocio | Validar módulo 11 del RUT |
| **7. URLs** | `farmasur/urls/{app}/` | Enrutamiento con DefaultRouter | Rutas automáticas para CRUD |
| **8. Forms** | `farmasur/forms/{app}/` | Formularios Django para templates | Validación en formularios HTML |
| **9. Tests** | `farmasur/tests/{app}/` | Pruebas unitarias e integración | Test de FEFO, test de autenticación |

## 📦 Importaciones Centralizadas

Cada capa tiene un `__init__.py` que agrupa las importaciones comunes:

```python
# Desde views
from farmasur.views import UsuarioViewSet, MedicamentoViewSet

# Desde models
from farmasur.models import Usuario, Medicamento, Receta

# Desde services
from farmasur.services import UsuarioService, calcular_fefo

# Desde permissions
from farmasur.permissions import IsAdmin, CanEditInventario
```

## 🚀 Flujo de una Solicitud

```
REQUEST (HTTP GET /api/medicamentos)
    ↓
farmacia_project/urls.py (incluye farmasur/urls/__init__.py)
    ↓
farmasur/urls/__init__.py (DefaultRouter → farmasur/views/inventario/views.py)
    ↓
farmasur/views/inventario/views.py (ViewSet → verificar permissions)
    ↓
farmasur/permissions/inventario/permissions.py (RBAC check)
    ↓
farmasur/serializers/inventario/serializers.py (validar datos)
    ↓
farmasur/services/inventario/services.py (lógica de negocio)
    ↓
farmasur/models/inventario/models.py (acceso a BD)
    ↓
RESPONSE (JSON con medicamentos)
```

## 🔄 Cambios Desde la Estructura Anterior

| Antes | Ahora | Beneficio |
|-------|-------|-----------|
| `usuarios/`, `inventario/`, `recetas/`, `ventas/` (apps separadas) | `farmasur/{models,views,serializers,services,...}` | Visión clara de responsabilidades, fácil navegación |
| `config/` | `farmacia_project/` | Nombre más descriptivo, alineado con convenciones |
| Rutas dispersas en cada app | `farmasur/urls/__init__.py` centralizado | Control central, fácil de auditar |
| Admin disperso | `farmasur/admin.py` centralizado | Un único lugar para administración |
| Tests dispersos | `farmasur/tests/{app}/` | Fácil de encontrar y ejecutar |

## ✅ Validación de Estructura

Ejecutar verificador:
```bash
python verify_farmasur.py
```

Resultado esperado:
```
✓ 10 capas creadas correctamente
✓ 40 archivos de lógica consolidados
✓ Rutas centralizadas en farmasur/urls/__init__.py
✓ Admin centralizado en farmasur/admin.py
✓ Importaciones funcionales
```
