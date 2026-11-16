#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificador de estructura por capas - Farmasur
Valida que la reorganización de capas esté completa
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Verifica la estructura de capas"""
    
    base_dir = Path(__file__).parent
    errors = []
    warnings = []
    
    print("\n" + "="*70)
    print("VERIFICANDO ESTRUCTURA POR CAPAS - FARMASUR")
    print("="*70)
    
    # 1. Verificar farmacia_project
    print("\n1. Verificando farmacia_project/...")
    farmacia_project_files = [
        'farmacia_project/__init__.py',
        'farmacia_project/settings.py',
        'farmacia_project/urls.py',
        'farmacia_project/asgi.py',
        'farmacia_project/wsgi.py',
        'farmacia_project/test_settings.py',
    ]
    
    for f in farmacia_project_files:
        path = base_dir / f
        if path.exists():
            print(f"   OK {f}")
        else:
            errors.append(f"ERROR: Falta {f}")
    
    # 2. Verificar capas en farmasur
    print("\n2. Verificando capas en farmasur/...")
    layers = [
        'models',
        'views',
        'serializers',
        'services',
        'permissions',
        'validators',
        'urls',
        'forms',
        'tests',
        'migrations',
        'static',
    ]
    
    for layer in layers:
        path = base_dir / 'farmasur' / layer
        if path.is_dir():
            has_init = (path / '__init__.py').exists()
            if has_init:
                print(f"   OK farmasur/{layer}/ con __init__.py")
            else:
                warnings.append(f"AVISO: farmasur/{layer}/ falta __init__.py")
        else:
            errors.append(f"ERROR: Falta capa farmasur/{layer}/")
    
    # 3. Verificar módulos por app
    print("\n3. Verificando modulos por app...")
    apps = ['usuarios', 'inventario', 'recetas', 'ventas']
    
    for layer in ['models', 'views', 'serializers', 'services', 'permissions', 'validators', 'urls', 'forms', 'tests']:
        for app in apps:
            app_path = base_dir / 'farmasur' / layer / app
            if app_path.is_dir():
                init_file = app_path / '__init__.py'
                if layer == 'tests':
                    main_file = app_path / f'test_{app}.py'
                else:
                    main_file = app_path / f'{layer.rstrip("s")}.py'  # singularizar
                
                if init_file.exists() and main_file.exists():
                    print(f"   OK farmasur/{layer}/{app}/ completo")
                else:
                    if not init_file.exists():
                        warnings.append(f"AVISO: farmasur/{layer}/{app}/__init__.py falta")
                    if not main_file.exists():
                        warnings.append(f"AVISO: farmasur/{layer}/{app}/{main_file.name} falta")
    
    # 4. Verificar archivos centralizados
    print("\n4. Verificando archivos centralizados...")
    central_files = [
        ('farmasur/__init__.py', 'Init principal'),
        ('farmasur/apps.py', 'Configuracion app'),
        ('farmasur/admin.py', 'Admin centralizado'),
        ('farmasur/urls/__init__.py', 'URLs centralizadas'),
    ]
    
    for file_path, description in central_files:
        path = base_dir / file_path
        if path.exists():
            print(f"   OK {description}: {file_path}")
        else:
            errors.append(f"ERROR: Falta {description}: {file_path}")
    
    # 5. Verificar manage.py
    print("\n5. Verificando manage.py...")
    manage_py = base_dir / 'manage.py'
    if manage_py.exists():
        with open(manage_py, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'farmacia_project.settings' in content:
                print("   OK manage.py apunta a farmacia_project.settings")
            else:
                errors.append("ERROR: manage.py no apunta a farmacia_project.settings")
    else:
        errors.append("ERROR: Falta manage.py")
    
    # 6. Verificar farmasur_templates
    print("\n6. Verificando farmasur_templates/...")
    templates_dir = base_dir / 'farmasur_templates'
    if templates_dir.is_dir():
        print(f"   OK Directorio farmasur_templates/ existe")
        template_files = list(templates_dir.glob('*.html'))
        if template_files:
            print(f"   OK Contiene {len(template_files)} archivos HTML")
        else:
            warnings.append("AVISO: farmasur_templates/ esta vacio")
    else:
        errors.append("ERROR: Falta directorio farmasur_templates/")
    
    # 7. Verificar que apps antiguas no existan
    print("\n7. Verificando que apps antiguas se eliminaron...")
    old_apps = ['usuarios', 'inventario', 'recetas', 'ventas']
    for app in old_apps:
        path = base_dir / app
        if not path.exists():
            print(f"   OK {app}/ eliminado (consolidado en farmasur)")
        else:
            errors.append(f"ERROR: App antigua aun existe: {app}/")
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE VERIFICACION")
    print("="*70)
    
    if not errors and not warnings:
        print("EXITO - ESTRUCTURA VERIFICADA CORRECTAMENTE!")
        print(f"   OK Farmacia Project")
        print(f"   OK 11 Capas")
        print(f"   OK 4 Modulos por capa")
        print(f"   OK Admin centralizado")
        print(f"   OK Templates centralizados")
        print(f"   OK Apps antiguas eliminadas")
        return 0
    else:
        if errors:
            print(f"\nERRORES ({len(errors)}):")
            for error in errors:
                print(f"   {error}")
        
        if warnings:
            print(f"\nAVISOS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")
        
        return 1

if __name__ == '__main__':
    sys.exit(check_structure())
