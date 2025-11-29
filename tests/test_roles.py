
import sys
import os
import unittest
from flask import Flask


# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.usuario import Usuario
from models.rol import Rol

class TestRoles(unittest.TestCase):
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
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_registration_cliente(self):
        response = self.client.post('/auth/register', data={
            'nombre': 'Test',
            'apellido': 'Cliente',
            'correo': 'cliente@test.com',
            'contrasena': 'password',
            'confirmar_contrasena': 'password',
            'telefono': '1234567890',
            'direccion': 'Test Address',
            'rol': '2'
        }, follow_redirects=True)
        
        # Check if user created with role 2
        user = Usuario.query.filter_by(correo='cliente@test.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.id_rol, 2)

    def test_registration_propietario(self):
        response = self.client.post('/auth/register', data={
            'nombre': 'Test',
            'apellido': 'Propietario',
            'correo': 'propietario@test.com',
            'contrasena': 'password',
            'confirmar_contrasena': 'password',
            'telefono': '1234567890',
            'direccion': 'Test Address',
            'rol': '3'
        }, follow_redirects=True)
        
        # Check if user created with role 3
        user = Usuario.query.filter_by(correo='propietario@test.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.id_rol, 3)

if __name__ == '__main__':
    unittest.main()
