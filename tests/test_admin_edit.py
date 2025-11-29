
import sys
import os
import unittest
from flask import Flask

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.usuario import Usuario
from models.rol import Rol
from datetime import date

class TestAdminUserEdit(unittest.TestCase):
    def setUp(self):
        # Force SQLite for testing
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create roles
        r1 = Rol(id_rol=1, nombre='Admin', descripcion='Admin')
        r2 = Rol(id_rol=2, nombre='Cliente', descripcion='Cliente')
        r3 = Rol(id_rol=3, nombre='Propietario', descripcion='Propietario')
        db.session.add_all([r1, r2, r3])
        
        # Create admin user
        self.admin = Usuario(
            nombre='Admin', apellido='User', correo='admin@test.com',
            contrasena='password', telefono='123', direccion='Test', id_rol=1,
            fecha_registro=date.today()
        )
        self.admin.set_password('password')
        
        # Create normal user to edit
        self.user = Usuario(
            nombre='Original', apellido='Name', correo='original@test.com',
            contrasena='password', telefono='123', direccion='Test', id_rol=2,
            fecha_registro=date.today()
        )
        self.user.set_password('password')
        
        db.session.add_all([self.admin, self.user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            correo=email,
            contrasena=password
        ), follow_redirects=True)

    def test_edit_user_fields(self):
        self.login('admin@test.com', 'password')
        
        # 1. Check that fields are NOT readonly in the form
        response = self.client.get(f'/admin/usuarios/{self.user.id_usuario}/editar')
        self.assertNotIn(b'readonly', response.data)
        
        # 2. Submit changes
        response = self.client.post(f'/admin/usuarios/{self.user.id_usuario}/editar', data={
            'nombre': 'Updated',
            'apellido': 'User',
            'correo': 'updated@test.com',
            'telefono': '999',
            'id_rol': '3' # Change to Propietario
        }, follow_redirects=True)
        
        self.assertIn(b'Usuario actualizado correctamente', response.data)
        
        # 3. Verify changes in DB
        updated_user = Usuario.query.get(self.user.id_usuario)
        self.assertEqual(updated_user.nombre, 'Updated')
        self.assertEqual(updated_user.correo, 'updated@test.com')
        self.assertEqual(updated_user.id_rol, 3)

if __name__ == '__main__':
    unittest.main()
