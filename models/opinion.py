from app import db


class Opinion(db.Model):
    __tablename__ = "opiniones"

    id_opinion = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(255))
    calificacion = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_objeto = db.Column(db.Integer, db.ForeignKey("objeto.id_objeto"), nullable=False)
