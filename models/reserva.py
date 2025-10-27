from app import db


class Reserva(db.Model):
    __tablename__ = "reserva"

    id_reserva = db.Column(db.Integer, primary_key=True)
    fecha_reserva = db.Column(db.Date, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_objeto = db.Column(db.Integer, db.ForeignKey("objeto.id_objeto"), nullable=False)

    pago = db.relationship("Pago", backref="reserva", uselist=False)
    incidencias = db.relationship("Incidencia", backref="reserva", lazy=True)
