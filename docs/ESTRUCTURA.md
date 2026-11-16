# FARMASUR - Estructura Completa del Proyecto

## 📁 Resumen de Carpetas y Archivos Creados

### Raíz del Proyecto
```
D:\progra\ProyectoIntegrado\
├── manage.py                 # Punto de entrada Django
├── requirements.txt          # Dependencias Python (actualizado)
├── SETUP.md                  # Guía de instalación detallada
├── README.md                 # Documentación principal
├── setup_database.sql        # Script SQL para PostgreSQL
├── setup_postgres.bat        # Script batch para Windows
├── setup_postgres.ps1        # Script PowerShell para Windows
├── .env.example              # Template de variables de entorno
├── .env.local                # Archivo local de desarrollo
├── .gitignore                # Archivos ignorados por Git
├── logs/                     # Logs de auditoría del sistema
├── templates/                # Plantillas HTML (a llenar)
├── media/                    # Archivos subidos
├── staticfiles/              # CSS, JS compilados
├── venv/                     # Virtualenv (creado por pip)
└── config/                   # Configuración Django
    ├── __init__.py
    ├── settings.py           # ✓ Actualizado para PostgreSQL
    ├── urls.py               # ✓ Actualizado
    ├── asgi.py
    └── wsgi.py
```

### Aplicaciones Django

#### 1. `usuarios/`
Autenticación, roles y auditoría.

```
usuarios/
├── migrations/               # Migraciones automáticas
│   ├── __init__.py
│   ├── 0001_initial.py
│   └── 0002_initial.py
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_farmacia.py  # ✓ Comando personalizado
├── __init__.py
├── models.py                 # ✓ Usuario, LogAuditoria
├── views.py
├── admin.py                  # ✓ Registros de admin
├── apps.py
├── forms.py
├── tests.py
└── urls.py
```

**Modelos principales:**
- `Usuario` - Autenticación personalizada con RUT (Módulo 11) y 4 roles
- `LogAuditoria` - Registro inmutable con hash SHA-256 encadenado

#### 2. `inventario/`
Gestión de medicamentos, lotes, FEFO y bodega.

```
inventario/
├── migrations/               # Migraciones automáticas
├── __init__.py
├── models.py                 # ✓ Producto, Lote, FEFO, Recepción
├── views.py
├── admin.py                  # ✓ Registros de admin
├── apps.py
├── forms.py
├── tests.py
└── urls.py
```

**Modelos principales:**
- `Laboratorio` - Proveedores de medicamentos
- `Producto` - Catálogo maestro con validación de condición de venta
- `Lote` - Gestión dual (vitrina + bodega) con FEFO
- `RecepcionProveedor` - Validación Orden vs Factura
- `Merma` - Registro de pérdidas y vencimientos

#### 3. `recetas/`
Validación de recetas médicas y medicamentos controlados.

```
recetas/
├── migrations/               # Migraciones automáticas
├── __init__.py
├── models.py                 # ✓ Receta, RecetaRetenidaISP, Unidosis
├── views.py
├── admin.py                  # ✓ Registros de admin
├── apps.py
├── forms.py
├── tests.py
└── urls.py
```

**Modelos principales:**
- `Receta` - Validación clínica con bloqueo a 30 días
- `RecetaRetenidaISP` - Libro Digital ISP (JSONB) con hash encadenado
- `UnidosisAsistencial` - Extracción de unidosis con validación de carnet

#### 4. `ventas/`
Punto de Venta, cajas diarias y comprobantes.

```
ventas/
├── migrations/               # Migraciones automáticas
├── __init__.py
├── models.py                 # ✓ CajaDiaria, POS, Convenio, Comprobante
├── views.py
├── admin.py                  # ✓ Registros de admin
├── apps.py
├── forms.py
├── tests.py
└── urls.py
```

**Modelos principales:**
- `CajaDiaria` - Apertura/cierre con validación de sesiones
- `POS` - Venta con integración FEFO y recetas retenidas
- `ConvenioIsapre` - Simulador de descuentos Isapre/Seguros
- `Comprobante` - Emisión de Boleta/Factura

---

## 🗄️ Base de Datos PostgreSQL

### Usuario de Base de Datos
- **Usuario:** `farmasur_user`
- **Contraseña:** `Farmasur2026!`
- **Base de Datos:** `farmasur_db`
- **Host:** `localhost`
- **Puerto:** `5432`

### Tablas Principales

#### usuarios
- `usuarios_usuario` - Usuarios con roles RBAC
- `usuarios_log_auditoria` - Registro de auditoría inmutable

#### inventario
- `inventario_laboratorio` - Proveedores
- `inventario_producto` - Catálogo maestro
- `inventario_lote` - Lotes con FEFO
- `inventario_recepcion_proveedor` - Recepción de cubetas
- `inventario_merma` - Pérdidas y vencimientos

#### recetas
- `recetas_receta` - Recetas médicas
- `recetas_receta_retenida_isp` - Libro ISP (con JSONField para datos inmutables)
- `recetas_unidosis_asistencial` - Unidosis con validación

#### ventas
- `ventas_caja_diaria` - Cajas diarias
- `ventas_pos` - Transacciones de venta
- `ventas_convenio_isapre` - Convenios simulador
- `ventas_comprobante` - Boletas/Facturas

---

## 🔑 Características Implementadas

### ✅ Autenticación y Seguridad
- [x] Autenticación personalizada con RUT chileno (Módulo 11)
- [x] 4 roles RBAC (Admin, Q.F., Técnico, Bodeguero)
- [x] Auditoría inmutable con hash SHA-256 encadenado
- [x] Protección CSRF, XSS mediante Django ORM
- [x] Hashing robusto de contraseñas (PBKDF2)

### ✅ Inventario
- [x] Catálogo maestro de productos
- [x] Gestión dual de stock (vitrina + bodega)
- [x] Algoritmo FEFO con `select_for_update()` para concurrencia
- [x] Bloqueo automático de lotes vencidos
- [x] Recepción de proveedores (Orden vs Factura)
- [x] Gestión de mermas

### ✅ Recetas y Medicamentos Controlados
- [x] Validación clínica de recetas médicas
- [x] Bloqueo automático a 30 días
- [x] Libro Digital ISP con JSONB (datos inmutables)
- [x] Hash encadenado para integridad
- [x] Extracción de unidosis asistencial

### ✅ Punto de Venta (POS)
- [x] Interfaz de venta con F2 rápido
- [x] Integración con lotes y FEFO
- [x] Apertura/cierre de cajas diarias
- [x] Validación de medicamentos controlados
- [x] Simulador Isapre/Seguros con descuentos variables
- [x] Emisión de Boleta/Factura

### ✅ Administración
- [x] Admin Django personalizado para todas las aplicaciones
- [x] Visualización de logs de auditoría
- [x] Gestión de convenios Isapre
- [x] CRUD de usuarios y roles

### ✅ Datos de Prueba
- [x] Comando `seed_farmacia` con:
  - 4 usuarios de prueba (cada rol)
  - 6 laboratorios
  - 7 medicamentos con múltiples lotes
  - 4 convenios Isapre
  - Cajas diarias de demostración

---

## 📝 Migraciones Generadas

```
usuarios:
  0001_initial.py     - Usuario, LogAuditoria
  0002_initial.py     - Relaciones y índices

inventario:
  0001_initial.py     - Modelos principales
  0002_initial.py     - Relaciones y índices

recetas:
  0001_initial.py     - Modelos principales
  0002_initial.py     - Relaciones y índices

ventas:
  0001_initial.py     - Modelos principales
  0002_initial.py     - Relaciones y índices
```

---

## 🚀 Próximos Pasos

1. **Instalar PostgreSQL 16+**
   - Windows: https://www.postgresql.org/download/windows/
   - Ejecutar: `setup_postgres.ps1` o `setup_postgres.bat`

2. **Crear la base de datos**
   ```bash
   python manage.py migrate
   ```

3. **Cargar datos de prueba**
   ```bash
   python manage.py seed_farmacia
   ```

4. **Iniciar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

5. **Acceder a**
   - Admin: http://localhost:8000/admin
   - Sitio web: http://localhost:8000 (a desarrollar)

---

## 📊 Configuración Django

### Variables de Entorno
- `DEBUG` - Modo desarrollo (True)
- `SECRET_KEY` - Clave secreta
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - PostgreSQL
- `ALLOWED_HOSTS` - Hosts permitidos
- `TIME_ZONE` - Zona horaria (America/Santiago)

### Aplicaciones Instaladas
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'usuarios',
    'inventario',
    'recetas',
    'ventas',
]
```

---

## 🎯 Checklist de Verificación

- [x] Estructura de carpetas creada
- [x] Modelos de datos definidos
- [x] Migraciones generadas
- [x] Admin Django configurado
- [x] Comando seed_farmacia creado
- [x] Dependencias en requirements.txt
- [x] Configuración PostgreSQL preparada
- [x] Scripts de setup (SQL, batch, PowerShell)
- [x] Documentación de instalación (SETUP.md)
- [x] Archivo .env.local para desarrollo

---

**Nota:** El proyecto está listo para instalar PostgreSQL y ejecutar las migraciones. Consulta `SETUP.md` para instrucciones detalladas.
