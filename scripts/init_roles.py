import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from models.rol import Rol


def init_roles():
    app = create_app()

    with app.app_context():
        # Verificar si ya existen roles
        if Rol.query.count() > 0:
            print("✅ Los roles ya existen en la base de datos:")
            for rol in Rol.query.all():
                print(f"   - {rol.nombre}: {rol.descripcion}")
            return

        # Crear roles base
        roles = [
            Rol(
                id_rol=1,
                nombre="Administrador",
                descripcion="Acceso completo al sistema, puede gestionar usuarios, categorías y moderar contenido",
            ),
            Rol(
                id_rol=2,
                nombre="Cliente",
                descripcion="Puede alquilar objetos de otros usuarios",
            ),
            Rol(
                id_rol=3,
                nombre="Propietario",
                descripcion="Puede publicar objetos para alquilarse",
            ),
        ]

        for rol in roles:
            db.session.add(rol)

        db.session.commit()
        print("✅ Roles inicializados correctamente:")
        print("   - Administrador: Acceso completo al sistema")
        print("   - Usuario: Puede publicar y alquilar objetos")

        # Mostrar conteo de usuarios por rol (para referencia)
        from models.usuario import Usuario

        user_count = Usuario.query.count()
        print(f"📊 Total de usuarios registrados: {user_count}")


if __name__ == "__main__":
    init_roles()
