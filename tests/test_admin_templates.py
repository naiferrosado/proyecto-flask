
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

class TestAdminTemplates(unittest.TestCase):
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
        
        # Create normal user
        self.user = Usuario(
            nombre='Normal', apellido='User', correo='user@test.com',
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

    def test_admin_usuarios_list(self):
        self.login('admin@test.com', 'password')
        response = self.client.get('/admin/usuarios')
        
        # Check for filter options
        self.assertIn(b'value="2">Clientes</option>', response.data)
        self.assertIn(b'value="3">Propietarios</option>', response.data)
        
        # Check for role badge
        self.assertIn(b'Cliente', response.data)

    def test_admin_edit_user(self):
        self.login('admin@test.com', 'password')
        response = self.client.get(f'/admin/usuarios/{self.user.id_usuario}/editar')
        
        # Check for select options
        self.assertIn(b'value="2" selected>Cliente</option>', response.data)
        self.assertIn(b'value="3" >Propietario</option>', response.data)

if __name__ == '__main__':
    unittest.main()
