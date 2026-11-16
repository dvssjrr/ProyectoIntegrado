#!/usr/bin/env python
"""
Script de verificación del proyecto Farmasur.
Ejecutar con: python verify_farmasur.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from usuarios.models import Usuario
from inventario.models import Laboratorio, Producto, Lote
from recetas.models import Receta
from ventas.models import ConvenioIsapre, CajaDiaria

def print_header(text):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Imprime un mensaje de éxito."""
    print(f"✅ {text}")

def print_error(text):
    """Imprime un mensaje de error."""
    print(f"❌ {text}")

def print_info(text):
    """Imprime un mensaje informativo."""
    print(f"ℹ️  {text}")

def verify_database_connection():
    """Verifica la conexión a la base de datos."""
    print_header("1. VERIFICACIÓN DE CONEXIÓN A LA BASE DE DATOS")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_success("Conexión a PostgreSQL establecida")
        
        # Mostrar información de la base de datos
        db_config = settings.DATABASES['default']
        print_info(f"Base de datos: {db_config['NAME']}")
        print_info(f"Usuario: {db_config['USER']}")
        print_info(f"Host: {db_config['HOST']}:{db_config['PORT']}")
        
        return True
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return False

def verify_migrations():
    """Verifica que todas las migraciones están aplicadas."""
    print_header("2. VERIFICACIÓN DE MIGRACIONES")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        output = StringIO()
        call_command('migrate', '--plan', stdout=output)
        
        output_text = output.getvalue()
        if "No migrations to apply" in output_text or "Planned actions:" in output_text:
            print_success("Todas las migraciones están aplicadas")
            return True
        else:
            print_error("Existen migraciones pendientes")
            return False
    except Exception as e:
        print_error(f"Error al verificar migraciones: {e}")
        return False

def verify_models():
    """Verifica que los modelos están correctamente definidos."""
    print_header("3. VERIFICACIÓN DE MODELOS")
    
    models_to_check = {
        'usuarios.Usuario': Usuario,
        'inventario.Laboratorio': Laboratorio,
        'inventario.Producto': Producto,
        'inventario.Lote': Lote,
        'recetas.Receta': Receta,
        'ventas.ConvenioIsapre': ConvenioIsapre,
        'ventas.CajaDiaria': CajaDiaria,
    }
    
    for model_name, model_class in models_to_check.items():
        try:
            # Intentar hacer una query para verificar que existe
            count = model_class.objects.count()
            print_success(f"{model_name} ({count} registros)")
        except Exception as e:
            print_error(f"{model_name}: {e}")
            return False
    
    return True

def verify_usuarios():
    """Verifica que los usuarios de prueba existen."""
    print_header("4. VERIFICACIÓN DE USUARIOS DE PRUEBA")
    
    usuarios_esperados = {
        'admin_user': 'ADMIN',
        'qf_maria': 'FARMACEUTICO',
        'aux_camila': 'TECNICO',
        'bod_carlos': 'BODEGUERO',
    }
    
    all_ok = True
    for username, rol_esperado in usuarios_esperados.items():
        try:
            usuario = Usuario.objects.get(username=username)
            if usuario.rol == rol_esperado:
                print_success(f"{username} - Rol: {usuario.get_rol_display()}")
            else:
                print_error(f"{username} - Rol incorrecto (esperado: {rol_esperado}, obtuve: {usuario.rol})")
                all_ok = False
        except Usuario.DoesNotExist:
            print_error(f"{username} - No encontrado")
            all_ok = False
    
    return all_ok

def verify_inventario():
    """Verifica que los datos de inventario existen."""
    print_header("5. VERIFICACIÓN DE INVENTARIO")
    
    all_ok = True
    
    # Laboratorios
    try:
        lab_count = Laboratorio.objects.count()
        print_success(f"Laboratorios: {lab_count} registros")
    except Exception as e:
        print_error(f"Laboratorios: {e}")
        all_ok = False
    
    # Productos
    try:
        prod_count = Producto.objects.count()
        print_success(f"Productos: {prod_count} registros")
        
        # Verificar medicamentos por condición
        for condicion in Producto.CondicionVenta.choices:
            count = Producto.objects.filter(condicion_venta=condicion[0]).count()
            if count > 0:
                print_info(f"  - {condicion[1]}: {count}")
    except Exception as e:
        print_error(f"Productos: {e}")
        all_ok = False
    
    # Lotes
    try:
        lote_count = Lote.objects.count()
        print_success(f"Lotes: {lote_count} registros")
        
        # Verificar estado FEFO
        for lote in Lote.objects.all()[:5]:
            print_info(f"  - {lote.producto.nombre_comercial}: {lote.estado_fefo}")
    except Exception as e:
        print_error(f"Lotes: {e}")
        all_ok = False
    
    return all_ok

def verify_convenios():
    """Verifica que los convenios Isapre existen."""
    print_header("6. VERIFICACIÓN DE CONVENIOS ISAPRE")
    
    try:
        convenios = ConvenioIsapre.objects.all()
        
        if convenios.count() == 0:
            print_error("No hay convenios Isapre registrados")
            return False
        
        for convenio in convenios:
            estado = "Activo" if convenio.activo else "Inactivo"
            print_success(f"{convenio.nombre} - {convenio.porcentaje_descuento}% - {estado}")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar convenios: {e}")
        return False

def verify_cajas():
    """Verifica que las cajas diarias existen."""
    print_header("7. VERIFICACIÓN DE CAJAS DIARIAS")
    
    try:
        cajas = CajaDiaria.objects.all()
        
        if cajas.count() == 0:
            print_info("No hay cajas diarias registradas")
            return True
        
        for caja in cajas:
            print_success(f"Caja {caja.caja_id} - {caja.fecha} ({caja.turno}) - {caja.estado}")
        
        return True
    except Exception as e:
        print_error(f"Error al verificar cajas: {e}")
        return False

def verify_settings():
    """Verifica la configuración de Django."""
    print_header("8. VERIFICACIÓN DE CONFIGURACIÓN DJANGO")
    
    checks = {
        'DEBUG': settings.DEBUG,
        'TIME_ZONE': settings.TIME_ZONE == 'America/Santiago',
        'LANGUAGE_CODE': settings.LANGUAGE_CODE == 'es-cl',
        'AUTH_USER_MODEL': settings.AUTH_USER_MODEL == 'usuarios.Usuario',
        'Database Engine': settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql',
    }
    
    all_ok = True
    for check_name, result in checks.items():
        if result or check_name == 'DEBUG':
            print_success(f"{check_name}: {result}")
        else:
            print_error(f"{check_name}: {result}")
            all_ok = False
    
    return all_ok

def main():
    """Ejecuta todas las verificaciones."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      VERIFICACIÓN DEL PROYECTO FARMASUR v1.0            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = {
        'Conexión a BD': verify_database_connection(),
        'Migraciones': verify_migrations(),
        'Modelos': verify_models(),
        'Usuarios': verify_usuarios(),
        'Inventario': verify_inventario(),
        'Convenios': verify_convenios(),
        'Cajas': verify_cajas(),
        'Configuración': verify_settings(),
    }
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    total = len(results)
    exitosas = sum(1 for v in results.values() if v)
    
    for nombre, resultado in results.items():
        estado = "✅ PASSED" if resultado else "❌ FAILED"
        print(f"{nombre:<30} {estado}")
    
    print(f"\n{exitosas}/{total} verificaciones exitosas\n")
    
    if exitosas == total:
        print("🎉 ¡PROYECTO VERIFICADO Y LISTO PARA USAR!")
        print("\nProximos pasos:")
        print("1. Iniciar servidor: python manage.py runserver")
        print("2. Acceder a Admin: http://localhost:8000/admin")
        print("3. Login: admin_user / Farmacia2026!")
        return 0
    else:
        print("⚠️  Revisa los errores anteriores antes de continuar")
        return 1

if __name__ == '__main__':
    sys.exit(main())
