# 🚀 COMANDOS RÁPIDOS - FARMASUR

## 🔧 Configuración Inicial

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con credenciales de BD
```

## 🗄️ Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations farmasur

# Aplicar migraciones
python manage.py migrate

# Crear usuario admin
python manage.py createsuperuser

# Resetear BD (destruye datos)
python manage.py flush
```

## 🏃 Desarrollo

```bash
# Iniciar servidor
python manage.py runserver

# Admin panel
http://localhost:8000/admin/

# API REST
http://localhost:8000/api/

# Listar todas las rutas
python manage.py show_urls
```

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
python manage.py test farmasur

# Con cobertura
coverage run --source='farmasur' manage.py test farmasur
coverage report
coverage html  # Generar reporte HTML

# Pruebas de un módulo
python manage.py test farmasur.tests.usuarios.tests
```

## 📊 Análisis y Validación

```bash
# Chequear código
python manage.py check

# Validar migraciones
python manage.py migrate --plan

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Generar fixtures (export datos)
python manage.py dumpdata farmasur > datos.json

# Cargar fixtures (import datos)
python manage.py loaddata datos.json
```

## 📝 Crear Nuevos Componentes

### Agregar un modelo nuevo
```bash
# 1. Crear en farmasur/models/{modulo}/models.py
# 2. Importar en farmasur/models/__init__.py
# 3. Registrar en farmasur/admin.py
# 4. Crear migración
python manage.py makemigrations farmasur
python manage.py migrate
```

### Agregar un endpoint nuevo
```bash
# 1. Crear ViewSet en farmasur/views/{modulo}/views.py
# 2. Crear Serializer en farmasur/serializers/{modulo}/serializers.py
# 3. Registrar en farmasur/urls/__init__.py
# 4. Importar en capas __init__.py correspondientes
# 5. Crear tests en farmasur/tests/{modulo}/test_views.py
```

### Crear una template nueva
```bash
# Crear en farmasur_templates/{modulo}/
# Usar {% extends 'base/base.html' %}
# Usar clases de Bootstrap 5
```

## 🐛 Debugging

```bash
# Shell interactivo Django
python manage.py shell

# Dentro del shell:
from farmasur.models import Usuario
usuarios = Usuario.objects.all()
usuario = usuarios.first()
print(usuario.rut, usuario.rol)
```

## 📦 Despliegue

```bash
# Generar requirements actualizado
pip freeze > requirements.txt

# Preparar para producción
DEBUG=False
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Usar gunicorn
gunicorn farmacia_project.wsgi:application --bind 0.0.0.0:8000
```

## 🔍 Troubleshooting

```bash
# Limpiar caché de Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Resetear BD (si hay conflictos)
python manage.py migrate farmasur zero
python manage.py makemigrations farmasur
python manage.py migrate

# Verificar estado del proyecto
python manage.py check
```

## 📱 Endpoints Principales

```
GET    /api/usuarios/              - Listar usuarios
POST   /api/usuarios/              - Crear usuario
GET    /api/usuarios/{id}/         - Ver usuario
PUT    /api/usuarios/{id}/         - Actualizar usuario
DELETE /api/usuarios/{id}/         - Eliminar usuario

GET    /api/medicamentos/          - Listar medicamentos
POST   /api/medicamentos/          - Crear medicamento
GET    /api/stock-vitrina/         - Ver stock en vitrina
GET    /api/stock-bodega/          - Ver stock en bodega
GET    /api/movimientos/           - Historial de movimientos

GET    /api/recetas/               - Listar recetas
POST   /api/recetas/               - Crear receta
GET    /api/libro-isp/             - Libro ISP (auditoría)

GET    /api/ventas/                - Listar ventas
POST   /api/ventas/                - Crear venta (punto de venta)
GET    /api/cajas/                 - Cajas diarias
```

---

**💡 Tip**: Consulta `CONVENCIONES.md` para estándares de código.
