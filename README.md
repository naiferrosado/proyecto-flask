# 🏗️ Rentflow

> **Plataforma de Alquiler de Objetos - Economía Circular en República Dominicana**

![Rentflow Banner](https://via.placeholder.com/1000x300?text=Rentflow+Banner) _<!-- Puedes reemplazar esto con una imagen real luego -->_

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

---

## 📖 Descripción

**Rentflow** es una solución innovadora diseñada para conectar a personas que tienen objetos subutilizados con aquellas que los necesitan temporalmente. Nuestra misión es promover el consumo responsable y la economía circular, facilitando el alquiler seguro y eficiente de todo tipo de artículos.

## 🚀 Características Principales

### � Gestión de Usuarios

- **Roles Diferenciados**:
  - 🛠️ **Administrador**: Control total del sistema, gestión de usuarios y moderación.
  - 🛍️ **Cliente**: Busca y alquila objetos.
  - 🏠 **Propietario**: Publica objetos y gestiona sus alquileres.
- **Seguridad**: Autenticación robusta y protección de rutas.
- **Perfiles**: Historial de reservas, pagos y reputación.

### � Gestión de Objetos

- **Publicación Sencilla**: Sube fotos y detalles de tus objetos.
- **Búsqueda Avanzada**: Filtros por categoría, precio y disponibilidad.
- **Galería de Imágenes**: Visualización atractiva de los productos.
- **Estados en Tiempo Real**: Disponible, Reservado, No disponible.

### 📅 Reservas y Pagos

- **Flujo de Reserva**: Solicitud -> Confirmación -> Pago -> Finalización.
- **Generación de Reportes**: Exportación de comprobantes en PDF (usando `xhtml2pdf`).
- **Historial de Transacciones**: Registro detallado de pagos y reservas.

## 🛠️ Stack Tecnológico

| Componente        | Tecnología                 | Descripción                          |
| ----------------- | -------------------------- | ------------------------------------ |
| **Backend**       | Python / Flask             | Lógica del servidor y API.           |
| **ORM**           | SQLAlchemy                 | Gestión de base de datos relacional. |
| **Base de Datos** | PostgreSQL                 | Almacenamiento robusto y escalable.  |
| **Frontend**      | HTML5 / CSS3 / Bootstrap 5 | Diseño responsivo y moderno.         |
| **Plantillas**    | Jinja2                     | Renderizado dinámico de vistas.      |
| **Reportes**      | xhtml2pdf                  | Generación de documentos PDF.        |

## ⚙️ Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local:

### 1. Prerrequisitos

- Python 3.8+
- PostgreSQL
- Git

### 2. Clonar el Repositorio

```bash
git clone https://github.com/naiferrosado/rentflow.git
cd rentflow
```

### 3. Configurar Entorno Virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=tu_clave_secreta_super_segura
DATABASE_URL=postgresql://usuario:password@localhost/rentflow
FLASK_ENV=development
```

### 6. Inicializar Base de Datos

```bash
flask db init
flask db migrate -m "Migración inicial"
flask db upgrade
```

### 7. Ejecutar la Aplicación

```bash
flask run
```

Visita `http://localhost:5000` en tu navegador.

## 📂 Estructura del Proyecto

```
rentflow/
├── app.py              # Punto de entrada de la aplicación
├── config/             # Configuraciones
├── models/             # Modelos de base de datos (SQLAlchemy)
├── src/
│   ├── forms/          # Formularios (WTForms)
│   └── routes/         # Controladores y rutas
├── static/             # Archivos estáticos (CSS, JS, Imágenes)
├── templates/          # Plantillas HTML (Jinja2)
├── migrations/         # Archivos de migración de base de datos
└── requirements.txt    # Dependencias del proyecto
```

## 👥 Autores

- **Naifer A. Rosado**
- **Ricardo Peña Garcia**

---

<div align="center">
  <sub>Hecho con ❤️ en República Dominicana</sub>
</div>
