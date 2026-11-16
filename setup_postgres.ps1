#!/usr/bin/env pwsh

<#
.SYNOPSIS
Script para crear la base de datos Farmasur en PostgreSQL

.DESCRIPTION
Este script configura PostgreSQL con:
- Usuario: farmasur_user
- Contraseña: Farmasur2026!
- Base de Datos: farmasur_db

.EXAMPLE
.\setup_postgres.ps1
#>

$PSqlPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
$PostgresUser = "postgres"
$HostName = "localhost"
$Port = "5432"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Farmasur - Configuracion de PostgreSQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que psql existe
if (-Not (Test-Path $PSqlPath)) {
    Write-Host "Error: No se encontro psql.exe en:" -ForegroundColor Red
    Write-Host $PSqlPath -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, verifica tu instalacion de PostgreSQL" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "Conectando a PostgreSQL..." -ForegroundColor Green
Write-Host ""

# Preparar el script SQL
$sqlScript = @"
-- Crear usuario
CREATE USER farmasur_user WITH PASSWORD 'Farmasur2026!';

-- Crear base de datos
CREATE DATABASE farmasur_db OWNER farmasur_user;

-- Conectar a la base de datos y dar permisos
ALTER DATABASE farmasur_db OWNER TO farmasur_user;
GRANT ALL PRIVILEGES ON DATABASE farmasur_db TO farmasur_user;
"@

# Guardar temporalmente
$tempSqlFile = "$PSScriptRoot\temp_setup.sql"
Set-Content -Path $tempSqlFile -Value $sqlScript -Encoding UTF8

try {
    # Ejecutar SQL
    & $PSqlPath -U $PostgresUser -h $HostName -p $Port -f $tempSqlFile
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Base de datos creada exitosamente" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora ejecuta en la carpeta del proyecto:" -ForegroundColor Yellow
    Write-Host "  python manage.py migrate" -ForegroundColor Cyan
    Write-Host "  python manage.py seed_farmacia" -ForegroundColor Cyan
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "Error al crear la base de datos:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica que PostgreSQL esta corriendo y accesible" -ForegroundColor Yellow
}
finally {
    # Limpiar archivo temporal
    if (Test-Path $tempSqlFile) {
        Remove-Item $tempSqlFile -Force -ErrorAction SilentlyContinue
    }
}

Read-Host "Presiona Enter para salir"
