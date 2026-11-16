# 🏥 FARMASUR v1.0
## Sistema Integral de Farmacia Privada - Chile

**Proyecto de Evaluación Integrada**
- Diego Arriagada
- Damian Bravo
- Antonio Guzmán

---

## 📋 Descripción

FARMASUR es un sistema completo de gestión farmacéutica con:
- ✅ Autenticación RUT con validación Módulo 11
- ✅ Inventario FEFO (First Expire First Out)
- ✅ Gestión de Recetas Médicas ISP
- ✅ Punto de Venta (POS) integrado
- ✅ Auditoría inmutable con SHA-256
- ✅ 4 Roles RBAC estrictos

---

## 🚀 Inicio Rápido

1. **Lee:** `docs/INICIO_RAPIDO.md`
2. **Instala:** PostgreSQL 16+
3. **Setup:** `.\setup_postgres.ps1`
4. **Ejecuta:**
   ```bash
   python manage.py migrate
   python manage.py seed_farmacia
   python manage.py runserver
   ```
5. **Accede:** http://localhost:8000/admin
   - Usuario: `admin_user`
   - Contraseña: `Farmacia2026!`

---

## 📂 Estructura

```
farmasur/
├── 📁 config/                    Configuración Django
│   ├── settings.py              Configuración de producción
│   ├── test_settings.py         Configuración de testing (SQLite)
│   ├── urls.py                  Rutas principales de API
│   ├── wsgi.py                  WSGI para producción
│   └── asgi.py                  ASGI para WebSocket
│
├── 📁 usuarios/                  Autenticación y roles
│   ├── models.py                Usuarios y auditoría
│   ├── views.py                 ViewSets de API
│   ├── serializers.py           Serializadores DRF
│   ├── services.py              Lógica de negocio
│   ├── permissions.py           Control RBAC
│   ├── validators.py            Validación RUT (Módulo 11)
│   ├── forms.py                 Formularios Django
│   ├── urls.py                  Rutas de usuarios
│   ├── admin.py                 Interfaz de administración
│   ├── migrations/              Historial de BD
│   └── tests.py                 Pruebas unitarias
│
├── 📁 inventario/               Gestión de medicamentos
│   ├── models.py                Laboratorio, Producto, Lote, Merma
│   ├── views.py                 ViewSets para CRUD
│   ├── serializers.py           Serializadores de inventario
│   ├── services.py              Lógica FEFO y stock
│   ├── permissions.py           Permisos de inventario
│   ├── validators.py            Validaciones
│   ├── forms.py                 Formularios
│   ├── urls.py                  Rutas
│   ├── admin.py                 Admin interface
│   ├── migrations/              Historial de BD
│   └── tests.py                 Pruebas
│
├── 📁 recetas/                  Recetas médicas ISP
│   ├── models.py                Receta, RecetaRetenidaISP, Unidosis
│   ├── views.py                 ViewSets
│   ├── serializers.py           Serializadores
│   ├── services.py              Lógica de recetas
│   ├── permissions.py           Permisos farmacéutico
│   ├── validators.py            Validaciones
│   ├── forms.py                 Formularios
│   ├── urls.py                  Rutas
│   ├── admin.py                 Admin interface
│   ├── migrations/              Historial de BD
│   └── tests.py                 Pruebas
│
├── 📁 ventas/                   Punto de Venta (POS)
│   ├── models.py                CajaDiaria, POS, Convenio, Comprobante
│   ├── views.py                 ViewSets
│   ├── serializers.py           Serializadores
│   ├── services.py              Lógica de cajas y ventas
│   ├── permissions.py           Permisos
│   ├── validators.py            Validaciones
│   ├── forms.py                 Formularios
│   ├── urls.py                  Rutas
│   ├── admin.py                 Admin interface
│   ├── migrations/              Historial de BD
│   └── tests.py                 Pruebas
│
├── 📁 farmasur_templates/       Plantillas HTML
├── 📁 farmasur_static/          CSS/JS compilados
├── 📁 farmasur_media/           Archivos subidos
├── 📁 logs/                     Auditoría y eventos
├── 📁 docs/                     Documentación (8 archivos)
│
├── manage.py                    Herramienta CLI de Django
├── requirements.txt             Dependencias Python
├── .env.example                 Variables de entorno ejemplo
├── .env.local                   Variables de entorno (local)
└── README.md                    Este archivo
```

---

## 📚 Documentación

Ver `docs/INDICE.md` para guía completa de documentación.

**Archivos principales:**
- `docs/INICIO_RAPIDO.md` - Instalación (5 min)
- `docs/SETUP.md` - Guía detallada
- `docs/ARQUITECTURA.md` - Diagramas y flujos
- `docs/REFERENCIA_RAPIDA.md` - Comandos útiles

---

## ✨ Características

| Feature | Detalle |
|---------|---------|
| **BD** | PostgreSQL 16+ |
| **Framework** | Django 5.0.1 |
| **API** | Django REST Framework |
| **Auth** | RUT + 4 Roles RBAC |
| **Inventario** | FEFO + Dual (vitrina/bodega) |
| **Auditoría** | SHA-256 encadenado |
| **Recetas** | ISP con JSONB |

---

## 🔧 Tecnología

- Python 3.12+
- Django 5.0.1
- PostgreSQL 16+
- Django REST Framework 3.14
- Tailwind CSS
- ReportLab (PDF)
- openpyxl (Excel)

---

## 📝 Licencia

Proyecto educativo - Evaluación Integrada 2026
