from app import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)

    objetos = db.relationship("Objeto", backref="usuario", lazy=True)
    reservas = db.relationship("Reserva", backref="usuario", lazy=True)
    opiniones = db.relationship("Opinion", backref="usuario", lazy=True)
    incidencias = db.relationship("Incidencia", backref="usuario", lazy=True)
