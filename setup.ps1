# Script de configuración del proyecto Farmasur
# Uso: .\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurando Proyecto Farmasur" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar Python
Write-Host "`n1. Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python no está instalado" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual
Write-Host "`n2. Creando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "✓ Entorno virtual ya existe" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "`n3. Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Entorno virtual activado" -ForegroundColor Green

# Instalar dependencias
Write-Host "`n4. Instalando dependencias..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    exit 1
}

# Configurar .env.local
Write-Host "`n5. Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".env.local")) {
    Copy-Item ".env.example" ".env.local"
    Write-Host "✓ Archivo .env.local creado (revisar configuración)" -ForegroundColor Green
} else {
    Write-Host "✓ Archivo .env.local ya existe" -ForegroundColor Green
}

# Verificar configuración de Django
Write-Host "`n6. Verificando configuración de Django..." -ForegroundColor Yellow
python manage.py check > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Configuración válida" -ForegroundColor Green
} else {
    Write-Host "ERROR: Problemas en la configuración" -ForegroundColor Red
    python manage.py check
    exit 1
}

# Crear migraciones y aplicarlas
Write-Host "`n7. Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migraciones aplicadas" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudieron aplicar las migraciones" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ Proyecto configurado exitosamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nPara iniciar el servidor, ejecutar:`n" -ForegroundColor Cyan
Write-Host "python manage.py runserver 0.0.0.0:8000" -ForegroundColor Yellow
Write-Host "`nURL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API: http://localhost:8000/api/`n" -ForegroundColor Yellow
