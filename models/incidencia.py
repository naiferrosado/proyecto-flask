from extensions import db


class Incidencia(db.Model):
    __tablename__ = "incidencias"

    id_incidencia = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Abierta")
    fecha_reporte = db.Column(db.Date, nullable=False)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_reserva = db.Column(
        db.Integer, db.ForeignKey("reserva.id_reserva"), nullable=False
    )
