import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate

# Cargar variables de entorno
load_dotenv()


def create_app():
    app = Flask(__name__)

    # CONFIGURACIÓN BÁSICA DE FLASK
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["DEBUG"] = os.getenv("FLASK_ENV") == "development"

    # CONFIGURACIÓN DE BASE DE DATOS
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_POOL_SIZE"] = int(os.getenv("DB_POOL_SIZE", 10))
    app.config["SQLALCHEMY_MAX_OVERFLOW"] = int(os.getenv("DB_MAX_OVERFLOW", 20))
    app.config["SQLALCHEMY_POOL_RECYCLE"] = int(os.getenv("DB_POOL_RECYCLE", 3600))

    # CONFIGURACIÓN DE SEGURIDAD
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["BCRYPT_LOG_ROUNDS"] = int(os.getenv("BCRYPT_LOG_ROUNDS", 12))

    # CONFIGURACIÓN DE LA APLICACIÓN
    app.config["APP_NAME"] = os.getenv("APP_NAME", "Rentflow")
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "./static/uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))
    app.config["SESSION_TIMEOUT"] = int(os.getenv("SESSION_TIMEOUT", 3600))

    # CONFIGURACIÓN DE EMAIL
    app.config["MAIL_SERVER"] = os.getenv("EMAIL_HOST")
    app.config["MAIL_PORT"] = int(os.getenv("EMAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("EMAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")

    # INICIALIZACIÓN DE EXTENSIONES
    db.init_app(app)
    migrate.init_app(app, db)

    # =============================================
    # REGISTRO DE BLUEPRINTS
    # =============================================
    register_blueprints(app)

    # =============================================
    # MANEJO DE ERRORES
    # =============================================
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    from routes.auth import auth_bp
    from routes.usuarios import usuarios_bp
    from routes.objetos import objetos_bp
    from routes.reservas import reservas_bp
    from routes.pagos import pagos_bp
    from routes.opiniones import opiniones_bp
    from routes.incidencias import incidencias_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
    app.register_blueprint(objetos_bp, url_prefix="/objetos")
    app.register_blueprint(reservas_bp, url_prefix="/reservas")
    app.register_blueprint(pagos_bp, url_prefix="/pagos")
    app.register_blueprint(opiniones_bp, url_prefix="/opiniones")
    app.register_blueprint(incidencias_bp, url_prefix="/incidencias")


def register_error_handlers(app):
    """Manejo personalizado de errores"""

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Recurso no encontrado"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Error interno del servidor"}, 500


# IMPORTACIÓN DE MODELOS (para migraciones)

from models.usuario import Usuario
from models.rol import Rol
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from models.objeto import Objeto
from models.incidencia import Incidencia
from models.categoria import Categoria

if __name__ == "__main__":
    app = create_app()

    host = os.getenv("SERVER_HOST", "localhost")
    port = int(os.getenv("SERVER_PORT", 5000))

    app.run(host=host, port=port, debug=app.config["DEBUG"])
