# FARMASUR — Sistema Integral de Farmacia Privada

## 🏥 Descripción

**Farmasur** es un sistema web integral desarrollado con Django 5, PostgreSQL 16 y Tailwind CSS para la gestión completa de una farmacia privada chilena. Implementa normativa ISP, FEFO (First Expire First Out), control de medicamentos retenidos, auditoría inmutable y matriz RBAC de 4 roles.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.12+, Django 5.x, Django REST Framework
- **Base de Datos:** PostgreSQL 16 (JSONB para documentos estructurados)
- **Frontend:** Django Templates + Tailwind CSS (CDN) + Alpine.js + Chart.js
- **Seguridad:** PBKDF2/Argon2, CSRF/XSS Protection, RBAC estricto, Auditoría SHA-256

---

## 📋 Requisitos Previos

1. **Python 3.12+** instalado
2. **PostgreSQL 16+** instalado y corriendo en `localhost:5432`
3. **pip** actualizado

---

## ⚙️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
cd D:\progra\ProyectoIntegrado
```

### 2. Crear Virtualenv (Opcional pero recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos PostgreSQL

#### Opción A: Usar psql (Recomendado)

Abre PowerShell y conectate como usuario postgres:

```bash
# Conectarse a PostgreSQL
psql -U postgres

# En la consola psql, ejecutar:
CREATE USER farmasur_user WITH PASSWORD 'Farmasur2026!';
CREATE DATABASE farmasur_db OWNER farmasur_user;
\c farmasur_db
GRANT ALL PRIVILEGES ON DATABASE farmasur_db TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO farmasur_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO farmasur_user;
\q
```

#### Opción B: Usar el script SQL incluido

```bash
psql -U postgres -f setup_database.sql
```

### 5. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario (Administrador)

```bash
python manage.py createsuperuser
```

Cuando pregunte por el RUT, usa: `123456789`

### 7. Cargar Datos de Prueba

```bash
python manage.py seed_farmacia
```

Este comando crea automáticamente:
- 4 usuarios de prueba (Admin, Q.F., Técnico, Bodeguero)
- 6 laboratorios farmacéuticos
- 7 medicamentos con múltiples lotes
- 4 convenios Isapre
- Cajas diarias de demostración

---

## 🚀 Iniciar el Servidor

```bash
python manage.py runserver
```

Accede a:
- **Sitio web:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin
- **API REST:** http://localhost:8000/api (próximamente)

---

## 👥 Usuarios de Prueba

| Usuario | Rol | Email | Contraseña |
|---------|-----|-------|-----------|
| `admin_user` | Administrador | admin@farmasur.cl | `Farmacia2026!` |
| `qf_maria` | Químico Farmacéutico | maria@farmasur.cl | `Farmacia2026!` |
| `aux_camila` | Técnico/Auxiliar | camila@farmasur.cl | `Farmacia2026!` |
| `bod_carlos` | Bodeguero | carlos@farmasur.cl | `Farmacia2026!` |

---

## 📊 Estructura de Aplicaciones Django

### `usuarios/`
- Autenticación personalizada con RUT (Módulo 11)
- Gestión de roles RBAC (4 perfiles)
- Auditoría inmutable con hash SHA-256

### `inventario/`
- Catálogo maestro de productos
- Gestión dual de inventario (vitrina + bodega)
- Algoritmo FEFO con `select_for_update()`
- Lotes con validación de vencimiento
- Recepción de proveedores (Orden vs Factura)
- Gestión de mermas

### `recetas/`
- Validación clínica de recetas médicas
- Bloqueo automático a 30 días
- Libro Digital ISP de Controlados (JSONB)
- Extracción de unidosis asistencial

### `ventas/`
- Punto de Venta (POS) con F2 rápido
- Apertura/cierre de cajas diarias
- Simulador de convenios Isapre/Seguros
- Emisión de Boleta/Factura
- Reporte de cajas diarias

---

## 🔐 Reglas de Negocio Críticas

### 1. Inventario Dual
- Cada producto tiene stock en **vitrina** (mostrador) y **bodega**
- Bloqueo automático de lotes vencidos o próximos a vencer

### 2. Algoritmo FEFO (First Expire First Out)
- Al procesar una venta, selecciona lotes por fecha de vencimiento
- Usa `transaction.atomic()` + `select_for_update()` para concurrencia
- Alertas visuales en FEFO crítico (< 15 días)

### 3. Medicamentos Controlados
- Requieren aprobación de Químico Farmacéutico
- Validación de RUT y N° Carnet del paciente
- Recetas válidas solo por **30 días**
- Registro inmutable en Libro ISP (JSONB con hash encadenado)

### 4. Simulador Isapre
- Integración con 4 convenios (Consalud, Colmena, Banmédica, Fonasa)
- Cálculo automático de descuento y copago
- Restricciones de medicamentos y montos

---

## 🎨 Paleta de Colores

| Uso | Color | Hex |
|-----|-------|-----|
| Primario | Sky 600 | `#0284C7` |
| Primario Claro | Sky 500 | `#0EA5E9` |
| Hover | Sky 400 | `#38BDF8` |
| Oscuro | Sky 700 | `#0369A1` |
| Fondo | Sky 50 | `#F0F9FF` |
| Sidebar | Azul Pizarra | `#0B192C` |
| FEFO Crítico | Rojo | `#DC2626` |
| FEFO Próximo | Ámbar | `#D97706` |
| FEFO Normal | Verde | `#16A34A` |

---

## 📚 Estructura de Carpetas

```
ProyectoIntegrado/
├── config/                      # Configuración Django
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # URLs globales
│   ├── wsgi.py
│   └── asgi.py
├── usuarios/                    # App: Autenticación y Roles
│   ├── models.py                # Usuario, LogAuditoria
│   ├── views.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_farmacia.py # Comando seed
├── inventario/                  # App: Gestión de Stock
│   ├── models.py                # Producto, Lote, FEFO
│   ├── views.py
│   └── admin.py
├── recetas/                     # App: Validación de Recetas
│   ├── models.py                # Receta, RecetaRetenidaISP
│   ├── views.py
│   └── admin.py
├── ventas/                      # App: Punto de Venta (POS)
│   ├── models.py                # CajaDiaria, POS, Comprobante
│   ├── views.py
│   └── admin.py
├── templates/                   # Plantillas HTML
├── staticfiles/                 # CSS, JS, Imágenes compiladas
├── media/                       # Archivos subidos
├── logs/                        # Logs de auditoría
├── manage.py
├── requirements.txt             # Dependencias Python
├── setup_database.sql           # Script SQL PostgreSQL
└── README.md                    # Este archivo
```

---

## 🧪 Pruebas y Validación

### Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Crear Usuario Admin Manual

```bash
python manage.py createsuperuser
```

### Acceder a Admin Django

Abre http://localhost:8000/admin y login con tus credenciales de superusuario.

---

## 📡 Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
SECRET_KEY=tu-secret-key-muy-seguro
DATABASE_URL=postgresql://farmasur_user:Farmasur2026!@localhost:5432/farmasur_db
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
TIME_ZONE=America/Santiago
```

---

## 🚨 Troubleshooting

### Error: "connection failed" PostgreSQL

**Causa:** PostgreSQL no está corriendo o credenciales incorrectas.

**Solución:**
```bash
# Verifica que PostgreSQL está corriendo
# En Windows: Verificar en Servicios o iniciar manualmente
# En Linux/Mac: sudo service postgresql start

# Verifica las credenciales en config/settings.py
psql -U farmasur_user -d farmasur_db -h localhost
```

### Error: "No such table: usuarios_usuario"

**Causa:** Migraciones no ejecutadas.

**Solución:**
```bash
python manage.py migrate
```

### Error: "FileNotFoundError: logs/"

**Causa:** Falta la carpeta logs.

**Solución:**
```bash
mkdir logs
```

---

## 📞 Contacto y Soporte

Para reportes de bugs o sugerencias, contacta con el equipo de desarrollo.

---

**Versión:** 1.0.0  
**Última actualización:** Noviembre 2026  
**Licencia:** Privada - Farmasur
