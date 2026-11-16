# Templates - Frontend HTML + Bootstrap

## 📁 Estructura

```
farmasur_templates/
  ├── base/                 # Templates base y generales
  │   └── base.html        # Template principal (extienden otros)
  │
  ├── usuarios/            # Templates de autenticación y usuarios
  │   ├── login.html
  │   ├── dashboard.html
  │   └── perfil.html
  │
  ├── inventario/          # Templates de medicamentos y stock
  │   ├── medicamentos.html
  │   ├── stock.html
  │   └── lotes.html
  │
  ├── recetas/             # Templates de recetas médicas
  │   ├── recetas.html
  │   └── dispensacion.html
  │
  └── ventas/              # Templates de punto de venta
      ├── pos.html
      ├── caja.html
      └── comprobantes.html
```

## 🎨 Convenciones

- **Base**: `{% extends 'base/base.html' %}`
- **Bootstrap 5**: Siempre usar clases de Bootstrap
- **Responsivo**: Diseño mobile-first
- **Comentarios HTML**: Solo para secciones complejas
- **Estructura**: 1 template por página principal

## 📌 Ejemplo

```html
{% extends 'base/base.html' %}

{% block title %}Usuarios - FARMASUR{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>Gestión de Usuarios</h1>
        <!-- Contenido aquí -->
    </div>
</div>
{% endblock %}
```
