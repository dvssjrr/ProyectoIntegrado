# Instrucciones de Configuración - Farmasur

## Requisitos Previos
- Python 3.14+
- pip (gestor de paquetes de Python)
- Git

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/dvssjrr/ProyectoIntegrado.git
cd ProyectoIntegrado
```

### 2. Crear y activar entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar `.env.example` a `.env.local` y actualizar según sea necesario:
```bash
copy .env.example .env.local
```

Variables disponibles en `.env.local`:
- `DEBUG`: Modo debug (True en desarrollo)
- `SECRET_KEY`: Clave secreta de Django
- `ALLOWED_HOSTS`: Hosts permitidos
- `USE_SQLITE`: Usar SQLite (True) o PostgreSQL (False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Configuración de BD

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver 0.0.0.0:8000
```

El servidor estará disponible en: `http://localhost:8000`

## Endpoints API

### Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario
- `GET /api/usuarios/{id}/` - Obtener usuario
- `PUT /api/usuarios/{id}/` - Actualizar usuario
- `DELETE /api/usuarios/{id}/` - Eliminar usuario

### Inventario
- `GET/POST /api/laboratorios/` - Laboratorios
- `GET/POST /api/productos/` - Productos
- `GET/POST /api/lotes/` - Lotes
- `GET/POST /api/mermas/` - Mermas

### Recetas
- `GET/POST /api/recetas/` - Recetas
- `GET /api/recetas/vigentes/` - Recetas vigentes
- `GET /api/recetas/vencidas/` - Recetas vencidas
- `GET/POST /api/recetas-retenidas/` - Recetas retenidas ISP
- `GET/POST /api/unidosis/` - Unidosis asistencial

### Ventas
- `GET/POST /api/cajas/` - Cajas diarias
- `GET/POST /api/ventas/` - Ventas POS
- `GET/POST /api/convenios/` - Convenios Isapre

## Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
python manage.py test

# Pruebas de un módulo específico
python manage.py test farmasur.tests.usuarios
```

## Validación del Proyecto

```bash
# Verificar configuración de Django
python manage.py check

# Crear migraciones (si es necesario)
python manage.py makemigrations
```

## Estructura del Proyecto

```
farmasur/
├── models/           # Modelos de datos (11 capas)
│   ├── usuarios/
│   ├── inventario/
│   ├── recetas/
│   └── ventas/
├── views/            # ViewSets de API REST
├── serializers/      # Serializadores
├── services/         # Lógica de negocio
├── permissions/      # Permisos personalizados
├── validators/       # Validadores
├── forms/            # Formularios (si se usan)
├── tests/            # Pruebas unitarias
└── admin.py          # Configuración admin
```

## Configuración de Base de Datos

### SQLite (Desarrollo)
Por defecto, el proyecto usa SQLite3:
```
db.sqlite3  # Se crea automáticamente
```

### PostgreSQL (Producción)
Para cambiar a PostgreSQL, actualizar `.env.local`:
```
USE_SQLITE=False
DB_NAME=farmasur_db
DB_USER=farmasur_user
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

## Troubleshooting

### Error: "Module not found"
Verificar que el entorno virtual está activado:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Error: "No changes detected"
Si no hay cambios de modelo nuevos, es normal:
```bash
python manage.py makemigrations --empty farmasur --name fix_initial
```

### Puerto 8000 en uso
```bash
python manage.py runserver 0.0.0.0:8001
```

## Desarrollo

### Crear nuevo modelo
1. Definir en `farmasur/models/{modulo}/models.py`
2. Importar en `farmasur/models/__init__.py`
3. Ejecutar: `python manage.py makemigrations`
4. Aplicar: `python manage.py migrate`

### Crear nuevo endpoint
1. Crear ViewSet en `farmasur/views/{modulo}/views.py`
2. Crear Serializer en `farmasur/serializers/{modulo}/serializers.py`
3. Registrar en router en `farmasur/urls/__init__.py`

## Soporte

Para reportar problemas o solicitar mejoras, crear un issue en GitHub.

---
**Última actualización**: Noviembre 2026
