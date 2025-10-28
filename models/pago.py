from extensions import db


class Pago(db.Model):
    __tablename__ = "pago"

    id_pago = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    metodo = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Completado")
    id_reserva = db.Column(
        db.Integer, db.ForeignKey("reserva.id_reserva"), nullable=False
    )
