from flask import Blueprint

# Crear el blueprint de autenticación
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    return "Página de login"


@auth_bp.route("/register")
def register():
    return "Página de registro"
