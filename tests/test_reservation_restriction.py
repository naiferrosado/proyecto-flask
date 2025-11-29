
import sys
import os
import unittest
from flask import Flask
from datetime import date, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.usuario import Usuario
from models.rol import Rol
from models.objeto import Objeto
from models.categoria import Categoria

class TestReservationRestrictions(unittest.TestCase):
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
        
        # Create category
        cat = Categoria(nombre='Test Cat', descripcion='Test')
        db.session.add(cat)
        db.session.commit()
        
        # Create users
        self.cliente = Usuario(
            nombre='Cliente', apellido='User', correo='cliente@test.com',
            contrasena='password', telefono='123', direccion='Test', id_rol=2,
            fecha_registro=date.today()
        )
        self.cliente.set_password('password')
        
        self.propietario = Usuario(
            nombre='Propietario', apellido='User', correo='propietario@test.com',
            contrasena='password', telefono='123', direccion='Test', id_rol=3,
            fecha_registro=date.today()
        )
        self.propietario.set_password('password')
        
        db.session.add_all([self.cliente, self.propietario])
        db.session.commit()
        
        # Create object
        self.objeto = Objeto(
            nombre='Test Obj', descripcion='Desc', precio=100.0,
            estado='Disponible', id_usuario=self.propietario.id_usuario,
            id_categoria=cat.id_categoria, fecha_publicacion=date.today()
        )
        db.session.add(self.objeto)
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

    def test_propietario_cannot_reserve(self):
        self.login('propietario@test.com', 'password')
        
        # Try to access reservation creation route
        response = self.client.post(f'/reservas/nueva/{self.objeto.id_objeto}', data={
            'fecha_inicio': date.today() + timedelta(days=1),
            'fecha_fin': date.today() + timedelta(days=2)
        }, follow_redirects=True)
        
        # Should be redirected to object detail with error
        self.assertIn(b'Los propietarios no pueden realizar reservas', response.data)
        
    def test_cliente_can_reserve(self):
        self.login('cliente@test.com', 'password')
        
        # Try to access reservation creation route
        response = self.client.post(f'/reservas/nueva/{self.objeto.id_objeto}', data={
            'fecha_inicio': date.today() + timedelta(days=1),
            'fecha_fin': date.today() + timedelta(days=2)
        }, follow_redirects=True)
        
        # Should be successful (redirect to list or payment)
        self.assertIn(b'Reserva creada exitosamente', response.data)

if __name__ == '__main__':
    unittest.main()
