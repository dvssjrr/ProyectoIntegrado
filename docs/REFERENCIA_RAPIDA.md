# 📚 REFERENCIA RÁPIDA - FARMASUR

## Comandos Esenciales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos PostgreSQL
.\setup_postgres.ps1  # Windows PowerShell
# O manualmente con psql

# Migraciones
python manage.py makemigrations   # Crear migraciones (si editas modelos)
python manage.py migrate          # Aplicar migraciones

# Cargar datos de prueba
python manage.py seed_farmacia

# Crear superusuario manual
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver

# Ejecutar pruebas
python manage.py test

# Verificar integridad
python verify_farmasur.py

# Consola interactiva de Django
python manage.py shell
```

---

## Rutas Importantes

| Ruta | Descripción |
|------|-------------|
| `http://localhost:8000/admin` | Admin Django |
| `http://localhost:8000` | Sitio web (en desarrollo) |
| `http://localhost:8000/api` | API REST (próximamente) |

---

## Usuarios de Prueba

```
Contraseña para todos: Farmacia2026!

admin_user   → Administrador   (admin@farmasur.cl)
qf_maria     → Q.F.            (maria@farmasur.cl)
aux_camila   → Técnico         (camila@farmasur.cl)
bod_carlos   → Bodeguero       (carlos@farmasur.cl)
```

---

## Configuración Base de Datos

```
DATABASE_URL: postgresql://farmasur_user:Farmasur2026!@localhost:5432/farmasur_db

Host: localhost
Port: 5432
User: farmasur_user
Pass: Farmasur2026!
DB:   farmasur_db
```

---

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `config/settings.py` | Configuración Django |
| `config/urls.py` | Rutas globales |
| `usuarios/models.py` | Modelos Usuario + Auditoría |
| `inventario/models.py` | Modelos FEFO + Inventario |
| `recetas/models.py` | Modelos Recetas + ISP |
| `ventas/models.py` | Modelos POS + Cajas |
| `usuarios/admin.py` | Admin de Usuarios |
| `inventario/admin.py` | Admin de Inventario |
| `recetas/admin.py` | Admin de Recetas |
| `ventas/admin.py` | Admin de Ventas |

---

## Estructura de Archivos Django

```
proyecto/
├── config/              # Configuración
│   ├── settings.py     # Principal (✓ actualizado)
│   ├── urls.py         # Rutas (✓ actualizado)
│   ├── wsgi.py
│   └── asgi.py
│
├── usuarios/            # App 1
│   ├── models.py       # Usuario, LogAuditoria
│   ├── views.py
│   ├── admin.py
│   ├── forms.py
│   └── management/
│       └── commands/
│           └── seed_farmacia.py
│
├── inventario/          # App 2
│   ├── models.py       # Laboratorio, Producto, Lote
│   ├── views.py
│   ├── admin.py
│   └── forms.py
│
├── recetas/             # App 3
│   ├── models.py       # Receta, RecetaRetenidaISP
│   ├── views.py
│   ├── admin.py
│   └── forms.py
│
├── ventas/              # App 4
│   ├── models.py       # CajaDiaria, POS, Comprobante
│   ├── views.py
│   ├── admin.py
│   └── forms.py
│
├── templates/           # Plantillas HTML
├── static/              # CSS, JS (en desarrollo)
├── media/               # Archivos subidos
├── logs/                # Logs de auditoría
│
├── manage.py           # Punto de entrada
├── requirements.txt    # Dependencias
├── .env.local          # Variables locales
├── .env.example        # Template
└── DOCUMENTACIÓN (5 archivos)
```

---

## Modelos Principales

### Usuario
```python
class Usuario(AbstractUser):
    rut              # Validado Módulo 11
    nombre_completo
    rol              # ADMIN, FARMACEUTICO, TECNICO, BODEGUERO
    activo
```

### Producto
```python
class Producto:
    sku_codigo_barra     # Único
    nombre_comercial
    precio_clp           # Entero (sin decimales)
    condicion_venta      # LIBRE, RECETA_SIMPLE, RECETA_RETENIDA
    stock_minimo_vitrina
```

### Lote
```python
class Lote:
    producto
    codigo_lote
    fecha_vencimiento    # Para FEFO
    stock_vitrina
    stock_bodega
    estado_fefo          # VENCIDO, CRÍTICO, PRÓXIMO, NORMAL
```

### Receta
```python
class Receta:
    folio
    rut_paciente
    fecha_emision
    estado               # VENCIDA si > 30 días
```

---

## Validaciones Importantes

| Validación | Dónde | Lógica |
|-----------|-------|--------|
| RUT Módulo 11 | Usuario.save() | Verifica dígito verificador |
| Receta 30 días | Receta.validar_vigencia_automatica() | Bloquea automático |
| FEFO | POS transacción | select_for_update() + ORDER BY vencimiento |
| Medicamento Controlado | POS validación | Requiere aprobación Q.F. |
| Stock suficiente | FEFO motor | Rollback si falta stock |

---

## Tablas de Referencia

### Condiciones de Venta
- LIBRE - Venta sin restricciones
- RECETA_SIMPLE - Requiere receta, sin bloqueo ISP
- RECETA_RETENIDA - Controlado, Libro ISP, > 30 días bloqueado

### Estados de Receta
- PENDIENTE - En espera de validación
- APROBADA - Autorizada para dispensar
- RECHAZADA - No cumple normativa
- DISPENSADA - Entregada al paciente
- VENCIDA - > 30 días (bloqueado automático)

### Estados FEFO
- NORMAL - Vigencia normal
- PRÓXIMO - 16-30 días para vencer
- CRÍTICO - < 15 días para vencer
- VENCIDO - Ya vencido (bloqueado)

### Estados de Caja
- ABIERTA - En operación
- CERRADA - Cierre manual completado
- SUSPENDIDA - Cierre sin validación

---

## Convenciones del Proyecto

| Aspecto | Convención |
|--------|------------|
| Nombres de Clase | PascalCase (Usuario, LogAuditoria) |
| Nombres de Variables | snake_case (rut, nombre_completo) |
| Nombres de BD | snake_case (usuarios_usuario) |
| Precios | Enteros CLP (sin decimales) |
| Fechas | YYYY-MM-DD (timezone-aware) |
| Timestamps | auto_now_add + auto_now |
| Booleanos | Siempre con default=False/True |
| JSONField | Para datos estructurados inmutables |
| Hash | SHA-256 de 64 caracteres |

---

## Atributos Globales del Proyecto

```python
# Zona horaria
TIME_ZONE = 'America/Santiago'

# Idioma
LANGUAGE_CODE = 'es-cl'

# Usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# Base de datos
DATABASE_ENGINE = 'django.db.backends.postgresql'

# Seguridad
ATOMIC_REQUESTS = True  # Todas las transacciones atómicas
```

---

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "No such table" | `python manage.py migrate` |
| Connection refused | Verificar PostgreSQL está corriendo |
| Import error | `pip install -r requirements.txt` |
| FileNotFoundError logs/ | `mkdir logs` |
| RUT inválido | Validar Módulo 11 (7-8 dígitos + verificador) |
| Migraciones pendientes | `python manage.py migrate` |

---

## URLs Útiles

- Docs Django: https://docs.djangoproject.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- DRF Docs: https://www.django-rest-framework.org/
- Tailwind CSS: https://tailwindcss.com/
- Alpine.js: https://alpinejs.dev/

---

## Versiones Requeridas

```
Python: 3.12+
Django: 5.0.1
PostgreSQL: 16+
pip: Última versión
psycopg: 3.3.9+
```

---

**Última actualización:** Noviembre 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para usar
