# 📝 CONVENCIONES DE CÓDIGO - FARMASUR v2.0

## ✅ Comentarios: Qué, Cuándo y Cómo

### ❌ MAL - Comentarios innecesarios
```python
# Incrementar contador
contador += 1

# Validar que el email existe
if email:
    enviar_confirmacion(email)
```

### ✅ BIEN - Comentarios útiles
```python
# Incrementar solo si es primera compra (aplica descuento)
contador += 1

# Enviar confirmación solo si se proporciona email alternativo
# (El email principal puede no tener acceso en este momento)
if email:
    enviar_confirmacion(email)
```

## 📂 Estructura de Capas - Responsabilidades Claras

### models/
**Qué**: Entidades y relaciones de BD (ORM)
**Regla**: Solo definiciones de campos, Meta, métodos simples

```python
class Usuario(AbstractUser):
    """Modelo de usuario con validación de RUT chileno."""
    rut = models.CharField(max_length=12, unique=True)
    
    class Meta:
        db_table = 'usuarios_usuario'
        ordering = ['-fecha_creacion']
```

### serializers/
**Qué**: Validación y transformación JSON ↔ Objetos
**Regla**: Incluir validaciones de negocio y lógica de transformación

```python
class UsuarioSerializer(serializers.ModelSerializer):
    """Serializa/valida datos de Usuario para API REST."""
    
    def validate_rut(self, value):
        # Validar RUT chileno (aquí va lógica de validación)
        if not es_rut_valido(value):
            raise serializers.ValidationError("RUT inválido")
        return value
```

### views/
**Qué**: Endpoints REST y coordinación de solicitudes
**Regla**: Solo cálculo de rutas, permisos y orquestación (delegar lógica a services)

```python
class UsuarioViewSet(viewsets.ModelViewSet):
    """Endpoints CRUD para usuarios."""
    
    def create(self, request):
        # Validar con serializer
        # Delegar lógica a service
        usuario = UsuarioService.crear_usuario(**datos)
        return Response(...)
```

### services/
**Qué**: Lógica de negocio reutilizable y operaciones transaccionales
**Regla**: Métodos estáticos con @transaction.atomic

```python
class UsuarioService:
    """Lógica centralizada de usuarios."""
    
    @staticmethod
    @transaction.atomic
    def crear_usuario(username, email, **kwargs):
        # Crear usuario + registrar auditoría + enviar email
        usuario = Usuario.objects.create_user(...)
        LogAuditoria.registrar(...)
        enviar_email_bienvenida(...)
        return usuario
```

### permissions/
**Qué**: Control de acceso basado en roles (RBAC)
**Regla**: Clases que heredan de BasePermission

```python
class EsAdmin(permissions.BasePermission):
    """Solo administradores."""
    
    def has_permission(self, request, view):
        return request.user.rol == Usuario.Rol.ADMIN
```

### validators/
**Qué**: Validaciones reutilizables de negocio
**Regla**: Funciones que lanzan ValidationError

```python
def validar_rut_chileno(value):
    """Valida RUT con Módulo 11."""
    if not es_valido(value):
        raise ValidationError("RUT inválido")
```

## 🎯 Importaciones - Usar __init__.py Centralizados

```python
# ❌ EVITAR
from farmasur.models.usuarios.models import Usuario
from farmasur.serializers.usuarios.serializers import UsuarioSerializer
from farmasur.views.usuarios.views import UsuarioViewSet

# ✅ USAR
from farmasur.models import Usuario
from farmasur.serializers import UsuarioSerializer
from farmasur.views import UsuarioViewSet
```

## 📝 Docstrings - Estilo Google

```python
def crear_usuario(username, email, **kwargs):
    """
    Crea un usuario con auditoría.
    
    Args:
        username (str): Nombre de usuario único
        email (str): Email del usuario
        **kwargs: Datos adicionales (nombre_completo, rol, etc)
    
    Returns:
        Usuario: Usuario creado
    
    Raises:
        ValueError: Si el username ya existe
    """
    pass
```

## 🔐 Seguridad - Checklist

- [ ] Nunca guardar credenciales en código
- [ ] Leer desde .env.local (usar python-decouple)
- [ ] Validar entrada de usuarios
- [ ] Protección CSRF en formularios
- [ ] Permisos en endpoints (no público por defecto)
- [ ] Registrar acciones críticas en auditoría

## 🧪 Testing - Una prueba por comportamiento

```python
class UsuarioTestCase(TestCase):
    """Pruebas para Usuario."""
    
    def test_crear_usuario_exitoso(self):
        """Crear usuario debe registrar en auditoría."""
        usuario = UsuarioService.crear_usuario(...)
        self.assertTrue(LogAuditoria.objects.filter(usuario=usuario).exists())
    
    def test_rut_invalido_lanza_error(self):
        """RUT con dígito verificador inválido debe rechazarse."""
        with self.assertRaises(ValueError):
            Usuario(rut='12345678-9').save()
```

## 📋 Checklist de Calidad

- [ ] Código tiene docstrings en funciones públicas
- [ ] Comentarios explican **por qué**, no **qué**
- [ ] Máximo 80 caracteres por línea
- [ ] No hay código comentado (eliminar o commit)
- [ ] Variables con nombres descriptivos
- [ ] Funciones < 30 líneas (si es más larga, refactorizar)
- [ ] Responsabilidades claras (cada capa tiene 1 propósito)
- [ ] Migraciones incluidas en commit
- [ ] Tests pasan y cobertura > 80%
- [ ] Sin credenciales en código

---

**Regla de Oro**: Si necesitas comentario para entender qué hace, el código está mal escrito.
Si necesitas comentario para entender **por qué** existe, está bien escrito.
