# 🚀 GUÍA DE INICIO RÁPIDO - FARMASUR

## Prerequisitos
✅ Python 3.12+  
✅ PostgreSQL 16+  
✅ pip actualizado  

---

## 1️⃣ Instalar Dependencias (60 segundos)

```bash
cd D:\progra\ProyectoIntegrado
pip install -r requirements.txt
```

---

## 2️⃣ Configurar PostgreSQL (3 minutos)

### Opción A: PowerShell (Recomendado en Windows)

```bash
# Desde PowerShell como administrador
.\setup_postgres.ps1
```

### Opción B: Batch Script

```bash
# Desde cmd como administrador
setup_postgres.bat
```

### Opción C: Manual con psql

```bash
# Abre PowerShell y conecta a PostgreSQL
psql -U postgres

# En la consola psql, ejecuta:
CREATE USER farmasur_user WITH PASSWORD 'Farmasur2026!';
CREATE DATABASE farmasur_db OWNER farmasur_user;
GRANT ALL PRIVILEGES ON DATABASE farmasur_db TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO farmasur_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO farmasur_user;
\q
```

---

## 3️⃣ Ejecutar Migraciones (30 segundos)

```bash
cd D:\progra\ProyectoIntegrado
python manage.py migrate
```

**Resultado esperado:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, inventario, recetas, 
  sessions, usuarios, ventas
Running migrations:
  Applying usuarios.0001_initial... OK
  Applying usuarios.0002_initial... OK
  ...
```

---

## 4️⃣ Cargar Datos de Prueba (15 segundos)

```bash
python manage.py seed_farmacia
```

**Resultado esperado:**
```
✓ Seed de datos completado exitosamente!

Usuarios de prueba creados:
  - username: admin_user | rol: ADMIN
  - username: qf_maria | rol: FARMACEUTICO
  - username: aux_camila | rol: TECNICO
  - username: bod_carlos | rol: BODEGUERO
```

---

## 5️⃣ Iniciar Servidor de Desarrollo (10 segundos)

```bash
python manage.py runserver
```

**Resultado esperado:**
```
Watching for file changes with StatReloader
Quit the server with CTRL-BREAK.
Starting development server at http://127.0.0.1:8000/
```

---

## 6️⃣ Acceder a la Aplicación

| Sección | URL | Usuario | Contraseña |
|---------|-----|---------|-----------|
| **Admin Django** | http://localhost:8000/admin | admin_user | Farmacia2026! |
| **Sitio Web** | http://localhost:8000 | (cualquiera) | Farmacia2026! |

---

## ✅ Usuarios de Prueba

```
┌─────────────┬────────────────────┬─────────────────────┐
│ Usuario     │ Rol                │ Email               │
├─────────────┼────────────────────┼─────────────────────┤
│ admin_user  │ Administrador      │ admin@farmasur.cl   │
│ qf_maria    │ Químico Farmacéutico│ maria@farmasur.cl  │
│ aux_camila  │ Técnico/Auxiliar   │ camila@farmasur.cl  │
│ bod_carlos  │ Bodeguero          │ carlos@farmasur.cl  │
└─────────────┴────────────────────┴─────────────────────┘
Contraseña para todos: Farmacia2026!
```

---

## 🔧 Troubleshooting Rápido

### ❌ Error: "connection failed" PostgreSQL

```bash
# Verifica que PostgreSQL está corriendo
# En Windows: Abre Servicios y busca "postgresql-x64-16"
# En Linux: sudo service postgresql status

# Verifica las credenciales
psql -U farmasur_user -d farmasur_db -h localhost
```

### ❌ Error: "No such table: usuarios_usuario"

```bash
# Ejecuta las migraciones nuevamente
python manage.py migrate
```

### ❌ Error: "FileNotFoundError: logs/"

```bash
# Crea la carpeta logs
mkdir logs
```

### ❌ Error: "psql.exe not found"

```bash
# Edita setup_postgres.ps1 o setup_postgres.bat
# Cambia la ruta de PostgreSQL según tu instalación
# Busca: "C:\Program Files\PostgreSQL\16\bin\psql.exe"
```

---

## 📊 Datos de Demostración

El comando `seed_farmacia` carga automáticamente:

- ✅ **4 usuarios** (cada rol RBAC)
- ✅ **6 laboratorios** (Laboratorio Chile, Bagó, Saval, Mintlab, Bayer, Pfizer)
- ✅ **7 medicamentos** con múltiples lotes:
  - Paracetamol 500mg (vitrina normal)
  - Ibuprofeno 400mg (lote próximo a vencer)
  - Amoxicilina 500mg (receta simple)
  - Clonazepam 0.5mg (controlado)
  - Tramadol 50mg (controlado)
  - Omeprazol 20mg (receta simple)
  - Vitamina C 1000mg (venta libre)
- ✅ **4 convenios Isapre** (Consalud, Colmena, Banmédica, Fonasa)
- ✅ **3 cajas diarias** de demostración

---

## 🎯 Próximas Acciones

1. **Explorar Admin Django**
   - Visualizar usuarios, productos, lotes
   - Verificar logs de auditoría
   - Crear nuevos medicamentos

2. **Revisar Modelos**
   - `usuarios/models.py` - RUT validado y auditoría
   - `inventario/models.py` - FEFO y lotes
   - `recetas/models.py` - Medicamentos controlados
   - `ventas/models.py` - POS y comprobantes

3. **Próximas Fases**
   - Crear vistas HTML con Tailwind CSS
   - Implementar lógica de POS (F2 rápido)
   - Crear API REST con Django REST Framework
   - Implementar reportes en PDF/Excel

---

## 📚 Documentación

- **SETUP.md** - Guía de instalación detallada
- **ESTRUCTURA.md** - Resumen de carpetas y modelos
- **config/settings.py** - Configuración de Django
- **Admin Django** - http://localhost:8000/admin

---

## 💡 Tips

- Presiona `Ctrl+Break` para detener el servidor
- Usa `python manage.py shell` para acceder a la consola de Django
- Ejecuta `python manage.py help` para ver todos los comandos disponibles
- Revisa los logs en la carpeta `logs/`

---

**¿Listo?** ¡Comienza con el Paso 1! 🚀
