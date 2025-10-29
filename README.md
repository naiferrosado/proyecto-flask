# proyecto-flask

🏗️ Rentflow - Plataforma de Alquiler de Objetos
Rentflow es una plataforma web que conecta a personas que tienen objetos con quienes los necesitan temporalmente, promoviendo la economía circular y el consumo responsable en la República Dominicana.

🚀 Características Principales
🔐 Autenticación y Usuarios
Registro e inicio de sesión seguro

Sistema unificado de roles: Los usuarios pueden publicar y alquilar objetos

Perfiles de usuario con reputación y calificaciones

Panel de administración para moderación

# 🛍️ Gestión de Objetos

Publicación de objetos para alquiler

Búsqueda avanzada con filtros por categoría, precio y ubicación

Galería de imágenes para cada objeto

Sistema de estados: Disponible, Reservado, No disponible

# 📅 Sistema de Reservas

Calendario de disponibilidad para cada objeto

Gestión de reservas con estados: Pendiente, Confirmada, Cancelada, Finalizada

Cálculo automático de costos basado en días de alquiler

# 💰 Pagos y Reputación

Sistema de pagos integrado (simulado)

Sistema de opiniones y calificaciones (1-5 estrellas)

Reputación de usuarios basada en transacciones

# 🛠️ Administración

Gestión de usuarios y verificación

Moderación de contenido (objetos, opiniones)

Gestión de categorías

Resolución de incidencias

# 🛠️ Tecnologías Utilizadas

# Backend

Python 3.8+ con Flask framework

Flask-SQLAlchemy para ORM de base de datos

Flask-Migrate para migraciones de BD

Flask-Login para autenticación

Flask-WTF para formularios seguros

PostgreSQL como base de datos principal

# Frontend

Bootstrap 5.1.3 para diseño responsive

Bootstrap Icons para iconografía

HTML5 + CSS3 con personalizaciones

Jinja2 para templates

Desarrollo y Despliegue
Git para control de versiones

Render/Railway para despliegue

Python-dotenv para variables de entorno

# 📦 Instalación y Configuración

Prerrequisitos

Python 3.8 o superior

PostgreSQL 12+

Git

1. Clonar el repositorio

git clone https://github.com/naiferrosado/rentflow.git
cd rentflow

2. Configurar entorno virtual

# Windows

python -m venv .venv
.venv\Scripts\activate

# Linux/Mac

python3 -m venv .venv
source .venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

4. Configurar variables de entorno

Crear archivo .env en la raíz del proyecto:

SECRET_KEY=tu_clave_secreta_muy_segura
DATABASE_URL=postgresql://usuario:password@localhost/rentflow
FLASK_ENV=development

5. Configurar base de datos

# Inicializar migraciones

flask db init

# Crear migración inicial

flask db migrate -m "Initial migration"

# Aplicar migraciones

flask db upgrade

6. Ejecutar la aplicación

# Desarrollo

python app.py

# O usando Flask

flask run

La aplicación estará disponible en http://localhost:5000

# 👤 Roles del Sistema

# Usuario Regular

Publicar objetos para alquiler

Alquilar objetos de otros usuarios

Gestionar sus propias reservas

Calificar a otros usuarios

# Administrador

Todas las funciones de usuario regular

Gestión completa de usuarios

Moderación de contenido

Gestión de categorías

Resolución de incidencias

# 🌟 Funcionalidades Futuras

Integración con APIs de pago reales

Sistema de mensajería entre usuarios

App móvil nativa

Sistema de notificaciones push

Geolocalización avanzada con mapas

Análisis de datos y reportes

Sistema de seguros para objetos

# 👥 Autores

Naifer A. Rosado

Ricardo Peña Garcia
