from extensions import db


class Rol(db.Model):
    __tablename__ = "rol"

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(100))

    usuarios = db.relationship("Usuario", backref="rol", lazy=True)

    def __repr__(self):
        return f"<Rol {self.nombre}>"
