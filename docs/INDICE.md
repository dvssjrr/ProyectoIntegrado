# 📖 ÍNDICE GENERAL - FARMASUR v1.0

## Documentación del Proyecto

Bienvenido al proyecto **FARMASUR** — Sistema Integral de Farmacia Privada. Esta es tu guía completa para comprender, instalar y ejecutar el sistema.

---

## 🚀 COMIENZA AQUÍ

### Para Instalar y Ejecutar (10 minutos)
1. **[INICIO_RAPIDO.md](./INICIO_RAPIDO.md)** ⭐ **LEE ESTO PRIMERO**
   - Instrucciones paso a paso
   - Instalación de PostgreSQL
   - Comandos Django esenciales
   - Verificación de integridad

### Para Instalar Detalladamente
2. **[SETUP.md](./SETUP.md)**
   - Requisitos previos
   - Configuración completa
   - Variables de entorno
   - Troubleshooting detallado

---

## 🏗️ ENTENDER LA ARQUITECTURA

3. **[ARQUITECTURA.md](./ARQUITECTURA.md)**
   - Diagrama de capas
   - Flujo de venta (POS)
   - Matriz RBAC completa
   - Estructura de base de datos
   - Pipeline de desarrollo

4. **[ESTRUCTURA.md](./ESTRUCTURA.md)**
   - Resumen de carpetas
   - Modelos por aplicación
   - Migraciones generadas
   - Características implementadas

---

## 📋 VERIFICACIÓN Y CHECKLIST

5. **[VERIFICACION.md](./VERIFICACION.md)**
   - Checklist completo
   - Estado del proyecto
   - Migraciones y datos
   - Deliverables finales

---

## 📚 REFERENCIA RÁPIDA

6. **[REFERENCIA_RAPIDA.md](./REFERENCIA_RAPIDA.md)** (Favoritos: Ctrl+D)
   - Comandos esenciales
   - Rutas importantes
   - Usuarios de prueba
   - Configuración de BD
   - Modelos principales
   - Troubleshooting rápido
   - Convenciones del proyecto

---

## 📂 ESTRUCTURA DE CARPETAS

```
D:\progra\ProyectoIntegrado\
│
├── 📋 DOCUMENTACIÓN (6 archivos .md)
│   ├── INICIO_RAPIDO.md         ⭐ Comienza aquí
│   ├── SETUP.md                 ✅ Instalación
│   ├── ESTRUCTURA.md            🏗️  Arquitectura
│   ├── ARQUITECTURA.md          📊 Diagramas
│   ├── VERIFICACION.md          ✓  Checklist
│   └── REFERENCIA_RAPIDA.md     📚 Referencia
│
├── 🐍 CÓDIGO PYTHON
│   ├── manage.py                # Punto de entrada
│   ├── verify_farmasur.py       # Script de verificación
│   │
│   ├── config/                  # Configuración Django
│   │   ├── settings.py          # ✅ Actualizado
│   │   ├── urls.py              # ✅ Actualizado
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── usuarios/                # App 1: Autenticación
│   │   ├── models.py            # Usuario, LogAuditoria
│   │   ├── admin.py             # Admin personalizado
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── seed_farmacia.py  # 📊 Datos de prueba
│   │   ├── tests.py             # Pruebas unitarias
│   │   └── migrations/          # 2 migraciones
│   │
│   ├── inventario/              # App 2: Gestión de Stock
│   │   ├── models.py            # Producto, Lote, FEFO
│   │   ├── admin.py             # Admin personalizado
│   │   ├── tests.py
│   │   └── migrations/          # 2 migraciones
│   │
│   ├── recetas/                 # App 3: Recetas Médicas
│   │   ├── models.py            # Receta, ISP, Unidosis
│   │   ├── admin.py             # Admin personalizado
│   │   ├── tests.py
│   │   └── migrations/          # 2 migraciones
│   │
│   └── ventas/                  # App 4: Punto de Venta
│       ├── models.py            # POS, Caja, Comprobante
│       ├── admin.py             # Admin personalizado
│       ├── tests.py
│       └── migrations/          # 2 migraciones
│
├── 📦 CONFIGURACIÓN
│   ├── requirements.txt          # 15 dependencias Python
│   ├── .env.example              # Template de variables
│   ├── .env.local                # Configuración local
│   ├── setup_database.sql        # Script SQL PostgreSQL
│   ├── setup_postgres.bat        # Setup Windows (batch)
│   ├── setup_postgres.ps1        # Setup Windows (PowerShell)
│   └── .gitignore
│
├── 📂 CARPETAS DE RUNTIME
│   ├── templates/                # Plantillas HTML (a llenar)
│   ├── media/                    # Archivos subidos
│   ├── staticfiles/              # CSS/JS compilados
│   ├── logs/                     # Logs de auditoría
│   └── venv/                     # Virtualenv
│
└── 📄 ARCHIVOS RAÍZ
    ├── README.md                 # Documentación principal
    └── manage.py                 # Django CLI

```

---

## 🎯 GUÍA POR PERFIL

### 👨‍💻 Desarrollador Nuevo
1. Lee: **INICIO_RAPIDO.md**
2. Instala: PostgreSQL + dependencias
3. Ejecuta: `python manage.py migrate`
4. Carga: `python manage.py seed_farmacia`
5. Explora: http://localhost:8000/admin
6. Lee: **ESTRUCTURA.md** para entender modelos

### 🏗️ Arquitecto de Software
1. Lee: **ARQUITECTURA.md** (diagramas y flujos)
2. Revisa: Modelos en `*/models.py`
3. Verifica: **VERIFICACION.md** (checklist)
4. Estudia: Validaciones y RBAC

### 🔧 DevOps / Infra
1. Lee: **SETUP.md** (configuración)
2. Revisa: `setup_postgres.ps1` / `setup_database.sql`
3. Configura: Variables de entorno
4. Deploya: Config para producción (próximo)

### 📊 Business Analyst
1. Lee: **ARQUITECTURA.md** (matriz RBAC y flujos)
2. Revisa: Modelos de datos
3. Consulta: **REFERENCIA_RAPIDA.md** (convenciones)

---

## 📈 Roadmap Implementación

```
✅ FASE 1: ESTRUCTURA (COMPLETADA)
   ├─ Modelos definidos (15)
   ├─ Migraciones generadas (8)
   ├─ Admin Django (8 apps)
   ├─ Datos de prueba
   ├─ Documentación completa
   └─ Setup PostgreSQL listo

⏳ FASE 2: FRONTEND (PRÓXIMA)
   ├─ Plantillas HTML con Tailwind CSS
   ├─ Dashboard ejecutivo
   ├─ POS con F2 rápido
   ├─ Responsivo (mobile + tablet)
   └─ Chart.js gráficos

⏳ FASE 3: API REST (PRÓXIMA)
   ├─ Endpoints AJAX
   ├─ DRF Serializers
   ├─ Autenticación Token
   └─ Paginación + Filtros

⏳ FASE 4: REPORTES (PRÓXIMA)
   ├─ PDF con ReportLab
   ├─ Excel con openpyxl
   ├─ Gráficos avanzados
   └─ Exportación automática

⏳ FASE 5: DEPLOYMENT (PRÓXIMA)
   ├─ Docker + docker-compose
   ├─ Gunicorn + Nginx
   ├─ SSL/TLS
   └─ CI/CD con GitHub Actions
```

---

## 🔑 Información Clave

### Base de Datos
```
Host:     localhost
Port:     5432
Usuario:  farmasur_user
Pass:     Farmasur2026!
DB:       farmasur_db
Engine:   PostgreSQL 16
```

### Usuarios de Prueba
```
admin_user   → ADMIN
qf_maria     → FARMACEUTICO
aux_camila   → TECNICO
bod_carlos   → BODEGUERO
Contraseña:  Farmacia2026! (todos)
```

### Rutas
```
Admin Django:  http://localhost:8000/admin
Sitio Web:     http://localhost:8000
API (próx):    http://localhost:8000/api
```

---

## 🚀 Inicio Rápido (60 segundos)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar PostgreSQL
.\setup_postgres.ps1

# 3. Migraciones
python manage.py migrate

# 4. Datos de prueba
python manage.py seed_farmacia

# 5. Iniciar servidor
python manage.py runserver

# 6. Acceder
# http://localhost:8000/admin
# Usuario: admin_user
# Contraseña: Farmacia2026!
```

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| PostgreSQL no conecta | Verificar que está corriendo + credenciales |
| "No such table" | Ejecutar: `python manage.py migrate` |
| Migraciones pendientes | Ejecutar: `python manage.py migrate` |
| Import errors | Ejecutar: `pip install -r requirements.txt` |
| Logs/ no existe | Ejecutar: `mkdir logs` |

---

## 📊 Estadísticas del Proyecto

```
Aplicaciones Django:    4
Modelos definidos:      15
Migraciones automáticas: 8
Tablas de BD:           15+
Índices de BD:          15+
Usuarios demo:          4
Medicamentos demo:      7
Lotes demo:             10+
Dependencias Python:    15
Líneas de código:       3000+
Archivos documentación: 6
```

---

## 🎓 Recursos Educativos

- **Django Official**: https://docs.djangoproject.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Tailwind CSS**: https://tailwindcss.com/
- **Alpine.js**: https://alpinejs.dev/
- **Chart.js**: https://www.chartjs.org/

---

## ✅ Checklist de Inicio

- [ ] Instalé PostgreSQL 16
- [ ] Ejecuté `setup_postgres.ps1`
- [ ] Ejecuté `python manage.py migrate`
- [ ] Ejecuté `python manage.py seed_farmacia`
- [ ] Ejecuté `python manage.py runserver`
- [ ] Accedí a http://localhost:8000/admin
- [ ] Login exitoso (admin_user / Farmacia2026!)
- [ ] Exploré Admin Django
- [ ] Revisé ESTRUCTURA.md

---

## 📝 Notas

- Todos los archivos `.md` están en el directorio raíz
- La base de datos se configura automáticamente con `setup_postgres.ps1`
- Los datos de prueba se cargan con `seed_farmacia`
- El proyecto usa Django 5.0.1 (última versión estable)
- PostgreSQL 16 es requerido (JSONB + UUID)

---

**Versión:** 1.0.0  
**Estado:** ✅ COMPLETO Y LISTO  
**Última actualización:** Noviembre 2026

---

## 🎉 ¡Bienvenido a FARMASUR!

Ahora estás listo para:
1. Instalar y ejecutar el proyecto
2. Explorar la arquitectura
3. Entender los modelos de datos
4. Contribuir al desarrollo

**¡Comienza leyendo INICIO_RAPIDO.md!**
