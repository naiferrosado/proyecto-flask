from extensions import db


class Objeto(db.Model):
    __tablename__ = "objeto"

    id_objeto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    estado = db.Column(db.String(20), nullable=False, default="Disponible")
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_categoria = db.Column(
        db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False
    )

    reservas = db.relationship("Reserva", backref="objeto", lazy=True)
    opiniones = db.relationship("Opinion", backref="objeto", lazy=True)
