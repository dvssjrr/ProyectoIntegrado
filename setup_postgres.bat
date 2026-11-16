@echo off
REM Script para crear la base de datos Farmasur en PostgreSQL
REM Debe ejecutarse como administrador o con permisos en PostgreSQL

echo.
echo ========================================
echo Farmasur - Configuracion de PostgreSQL
echo ========================================
echo.

REM Pedir la ruta de PostgreSQL
set "PSQL_PATH=C:\Program Files\PostgreSQL\16\bin\psql.exe"

REM Verificar si existe
if not exist "%PSQL_PATH%" (
    echo Error: No se encontro psql.exe en %PSQL_PATH%
    echo Por favor, verifica tu instalacion de PostgreSQL
    pause
    exit /b 1
)

echo Conectando a PostgreSQL...
echo.

REM Ejecutar comandos SQL
"%PSQL_PATH%" -U postgres -h localhost -p 5432 << EOF
-- Crear usuario
CREATE USER farmasur_user WITH PASSWORD 'Farmasur2026!';

-- Crear base de datos
CREATE DATABASE farmasur_db OWNER farmasur_user;

-- Conectar a la base de datos
\c farmasur_db

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE farmasur_db TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO farmasur_user;

-- Extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Permisos finales
GRANT ALL ON SCHEMA public TO farmasur_user;

EOF

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ^✓ Base de datos creada exitosamente
    echo ========================================
    echo.
    echo Ahora ejecuta en la carpeta del proyecto:
    echo   python manage.py migrate
    echo   python manage.py seed_farmacia
    echo.
) else (
    echo.
    echo Error al crear la base de datos
    echo Verifica que PostgreSQL esta corriendo
    echo.
)

pause
