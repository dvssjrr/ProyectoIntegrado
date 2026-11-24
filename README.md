# FARMASUR v2.0
Sistema de Gestión Farmacéutica Integral - Chile

## Estructura del Proyecto

```
farmacia_project/          # Configuración de Django (settings, urls, wsgi, asgi)
farmasur/                  # App principal organizada en 11 capas
  ├── models/              # Modelos de BD (ORM Django)
  ├── views/               # ViewSets de API REST
  ├── serializers/         # Validación de datos JSON
  ├── services/            # Lógica de negocio reutilizable
  ├── permissions/         # Control de acceso (RBAC)
  ├── validators/          # Validaciones personalizadas
  ├── urls/                # Enrutamiento de endpoints
  ├── forms/               # Formularios Django
  ├── tests/               # Pruebas unitarias y de integración
  ├── migrations/          # Versionado de BD
  ├── static/              # CSS, JS, imágenes
  ├── admin.py             # Interfaz de administración
  └── apps.py              # Configuración de app
  
farmasur_templates/        # Templates HTML + Bootstrap (Frontend)
```

## Quick Start

### 1. Configurar Variables de Entorno
```bash
cp .env.example .env.local
# Editar .env.local con credenciales de BD
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Migraciones y BD
```bash
python manage.py makemigrations farmasur
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecutar Servidor
```bash
python manage.py runserver
```

**Admin**: http://localhost:8000/admin/
**API**: http://localhost:8000/api/

### Varias cuentas en el mismo navegador

Para usar cuentas distintas en ventanas separadas del mismo perfil del navegador, inicia sesión en la primera ventana y abre **Más opciones** en el área de la cuenta; luego elige **Abrir sesión con otro usuario**. La nueva ventana tendrá una sesión independiente; duplicar una pestaña normal seguirá compartiendo la sesión actual.

## Acceso, clientes y reportes

- El personal inicia sesion con correo electronico y contrasena; el nombre de usuario se conserva para compatibilidad con cuentas anteriores.
- Las fichas de clientes son independientes de las cuentas de empleados. El RUT permite recuperar sus datos, convenio y compras previas desde el POS.
- Las ventas de productos con receta requieren una receta aprobada y vigente, RUT coincidente y confirmacion de una cuenta Quimico Farmaceutico.
- Los pagos con tarjeta y BancoEstado son una simulacion local; no se procesa ni almacena informacion de tarjetas reales.
- Los administradores pueden consultar reportes de ventas y auditoria de sesiones. La auditoria conserva el usuario, nombre, RUT, direccion IP, hora y agente de usuario.
- Los reportes permiten imprimir el PDF completo o exportar a PDF/Excel todas las ventas filtradas o solo las seleccionadas.
- Tras actualizar el codigo, ejecutar `python manage.py migrate` para crear las nuevas tablas y campos.

## Capas del Proyecto

| Capa | Propósito |
|------|-----------|
| **models** | Entidades y relaciones de BD |
| **views** | Endpoints REST (GET, POST, PUT, DELETE) |
| **serializers** | Validación y transformación JSON ↔ Objetos |
| **services** | Lógica de negocio centralizada |
| **permissions** | Control de acceso por rol |
| **validators** | Validaciones reutilizables |
| **urls** | Rutas y enrutamiento automático |
| **forms** | Formularios Django |
| **tests** | Pruebas unitarias |
| **migrations** | Control de versiones de BD |
| **static** | Archivos estáticos (CSS, JS, imágenes) |

## Módulos Principales

- **usuarios**: Autenticación, roles, auditoría
- **inventario**: Medicamentos, stock, lotes, movimientos
- **recetas**: Recetas médicas, dispensación
- **ventas**: Punto de venta, caja, comprobantes

## Convenciones de Código

### Modelos
```python
# Siempre incluyen timestamps y tabla personalizada
class MiModelo(models.Model):
    campo = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mimodelo_mimodelo'
        ordering = ['-fecha_creacion']
```

### Importaciones desde Capas
```python
# En lugar de:
from farmasur.models.usuarios.models import Usuario

# Usa:
from farmasur.models import Usuario
from farmasur.serializers import UsuarioSerializer
from farmasur.views import UsuarioViewSet
```

### Comentarios
- Comenta **por qué**, no **qué** (el código ya dice qué)
- Usa docstrings en clases y funciones
- Máximo 1-2 líneas por comentario

## Testing

```bash
# Ejecutar todas las pruebas
python manage.py test farmasur

# Con cobertura
coverage run --source='farmasur' manage.py test farmasur
coverage report
```

## Variables de Entorno

```env
# .env.local
SECRET_KEY=tu-clave-secreta
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=farmasur_db
DB_USER=farmasur_user
DB_PASSWORD=contraseña-segura
DB_HOST=localhost
DB_PORT=5432
```

## Autores

- Diego Arriagada
- Damian Bravo 

**Proyecto de Evaluación Integrada**
