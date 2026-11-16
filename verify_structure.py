"""
Script para verificar la integridad de la estructura del proyecto FARMASUR.
Valida que todos los archivos necesarios existan en sus ubicaciones correctas.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_FILES = {
    # Config
    'config': [
        'settings.py',
        'test_settings.py',
        'urls.py',
        'wsgi.py',
        'asgi.py',
    ],
    # Apps
    'usuarios': [
        'models.py',
        'views.py',
        'serializers.py',
        'services.py',
        'permissions.py',
        'validators.py',
        'forms.py',
        'urls.py',
        'admin.py',
        'tests.py',
    ],
    'inventario': [
        'models.py',
        'views.py',
        'serializers.py',
        'services.py',
        'permissions.py',
        'validators.py',
        'forms.py',
        'urls.py',
        'admin.py',
        'tests.py',
    ],
    'recetas': [
        'models.py',
        'views.py',
        'serializers.py',
        'services.py',
        'permissions.py',
        'validators.py',
        'forms.py',
        'urls.py',
        'admin.py',
        'tests.py',
    ],
    'ventas': [
        'models.py',
        'views.py',
        'serializers.py',
        'services.py',
        'permissions.py',
        'validators.py',
        'forms.py',
        'urls.py',
        'admin.py',
        'tests.py',
    ],
}

REQUIRED_DIRS = [
    'config',
    'usuarios',
    'inventario',
    'recetas',
    'ventas',
    'farmasur_templates',
    'farmasur_static',
    'farmasur_media',
    'logs',
    'docs',
]


def verify_structure():
    """Verifica la estructura completa del proyecto."""
    print("=" * 60)
    print("[*] Verificando estructura de FARMASUR")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Verificar directorios
    print("\n[Directorios]")
    for dirname in REQUIRED_DIRS:
        dirpath = BASE_DIR / dirname
        if dirpath.exists() and dirpath.is_dir():
            print(f"  [OK] {dirname}/")
        else:
            errors.append(f"Directorio faltante: {dirname}/")
            print(f"  [ERROR] {dirname}/")
    
    # Verificar archivos por app
    print("\n[Archivos]")
    for app_name, files in REQUIRED_FILES.items():
        app_dir = BASE_DIR / app_name
        
        for filename in files:
            filepath = app_dir / filename
            if filepath.exists():
                print(f"  [OK] {app_name}/{filename}")
            else:
                errors.append(f"Archivo faltante: {app_name}/{filename}")
                print(f"  [ERROR] {app_name}/{filename}")
    
    # Verificar migrations
    print("\n[Migraciones]")
    for app_name in REQUIRED_FILES.keys():
        if app_name == 'config':
            continue
        
        mig_dir = BASE_DIR / app_name / 'migrations'
        init_file = mig_dir / '__init__.py'
        
        if mig_dir.exists() and init_file.exists():
            print(f"  [OK] {app_name}/migrations/")
        else:
            warnings.append(f"Directorio migrations incompleto: {app_name}/migrations/")
            print(f"  [WARN] {app_name}/migrations/")
    
    # Resumen
    print("\n" + "=" * 60)
    if not errors:
        print("[SUCCESS] ESTRUCTURA VERIFICADA CORRECTAMENTE")
        if warnings:
            print(f"[WARN] {len(warnings)} advertencia(s):")
            for w in warnings:
                print(f"   - {w}")
    else:
        print(f"[ERROR] SE ENCONTRARON {len(errors)} ERRORES:")
        for e in errors:
            print(f"   - {e}")
        return False
    
    print("=" * 60)
    return not bool(errors)


if __name__ == '__main__':
    success = verify_structure()
    exit(0 if success else 1)
