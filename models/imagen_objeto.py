from extensions import db


class ImagenObjeto(db.Model):
    __tablename__ = "imagen_objeto"

    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    objeto_id = db.Column(db.Integer, db.ForeignKey("objeto.id_objeto"), nullable=False)
