
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.rol import Rol

app = create_app()

with app.app_context():
    # 1. Rename role 2 from 'Usuario' to 'Cliente'
    rol_usuario = Rol.query.get(2)
    if rol_usuario:
        if rol_usuario.nombre != 'Cliente':
            print(f"Renaming role '{rol_usuario.nombre}' to 'Cliente'...")
            rol_usuario.nombre = 'Cliente'
            rol_usuario.descripcion = 'Usuario que puede rentar objetos'
            db.session.commit()
            print("Role renamed successfully.")
        else:
            print("Role 2 is already named 'Cliente'.")
    else:
        print("Role 2 not found. Creating 'Cliente' role...")
        rol_cliente = Rol(id_rol=2, nombre='Cliente', descripcion='Usuario que puede rentar objetos')
        db.session.add(rol_cliente)
        db.session.commit()
        print("Role 'Cliente' created.")

    # 2. Create role 3 'Propietario' if it doesn't exist
    rol_propietario = Rol.query.get(3)
    if not rol_propietario:
        print("Creating 'Propietario' role...")
        rol_propietario = Rol(id_rol=3, nombre='Propietario', descripcion='Usuario que puede publicar y rentar objetos')
        db.session.add(rol_propietario)
        db.session.commit()
        print("Role 'Propietario' created.")
    else:
        print("Role 3 'Propietario' already exists.")

    print("Roles update complete.")
