# make_admin.py
import sys

sys.path.append(".")

from app import create_app, db
from models.usuario import Usuario

app = create_app()
with app.app_context():
    usuario = Usuario.query.filter_by(correo="naifer@gmail.com").first()
    if usuario:
        usuario.id_rol = 1
        db.session.commit()
        print("✅ Tu usuario ahora es administrador")
    else:
        print("❌ Usuario no encontrado")
