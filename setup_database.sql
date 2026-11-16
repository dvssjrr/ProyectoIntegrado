-- Script para crear la base de datos y usuario de Farmasur en PostgreSQL
-- Ejecutar como superusuario (postgres)

-- Crear usuario con contraseña
CREATE USER farmasur_user WITH PASSWORD 'Farmasur2026!';

-- Crear base de datos
CREATE DATABASE farmasur_db OWNER farmasur_user;

-- Conceder permisos
GRANT ALL PRIVILEGES ON DATABASE farmasur_db TO farmasur_user;

-- Conectar a la base de datos y hacer configuraciones adicionales
\c farmasur_db

-- Permitir que el usuario cree esquemas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO farmasur_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO farmasur_user;

-- Extención recomendada para JSON
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Dar permisos totales en el schema public
GRANT ALL ON SCHEMA public TO farmasur_user;
