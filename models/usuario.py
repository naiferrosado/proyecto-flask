# models/usuario.py
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)

    objetos = db.relationship("Objeto", backref="usuario", lazy=True)
    reservas = db.relationship("Reserva", backref="usuario", lazy=True)
    opiniones = db.relationship("Opinion", backref="usuario", lazy=True)
    incidencias = db.relationship("Incidencia", backref="usuario", lazy=True)

    # Métodos requeridos por Flask-Login
    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena, password)
