#!/bin/bash
# Script de configuración del proyecto Farmasur
# Uso: bash setup.sh

set -e

echo "========================================"
echo "Configurando Proyecto Farmasur"
echo "========================================"

# Verificar Python
echo -e "\n1. Verificando Python..."
python3 --version || { echo "ERROR: Python no está instalado"; exit 1; }

# Crear entorno virtual
echo -e "\n2. Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo -e "\n3. Activando entorno virtual..."
source venv/bin/activate
echo "✓ Entorno virtual activado"

# Instalar dependencias
echo -e "\n4. Instalando dependencias..."
pip install -q -r requirements.txt
echo "✓ Dependencias instaladas"

# Configurar .env.local
echo -e "\n5. Configurando variables de entorno..."
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo "✓ Archivo .env.local creado (revisar configuración)"
else
    echo "✓ Archivo .env.local ya existe"
fi

# Verificar configuración de Django
echo -e "\n6. Verificando configuración de Django..."
python manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Configuración válida"
else
    echo "ERROR: Problemas en la configuración"
    python manage.py check
    exit 1
fi

# Crear migraciones y aplicarlas
echo -e "\n7. Aplicando migraciones..."
python manage.py migrate
echo "✓ Migraciones aplicadas"

echo -e "\n========================================"
echo "✓ Proyecto configurado exitosamente"
echo "========================================"
echo -e "\nPara iniciar el servidor, ejecutar:\n"
echo "python manage.py runserver 0.0.0.0:8000"
echo -e "\nURL: http://localhost:8000"
echo "API: http://localhost:8000/api/"
