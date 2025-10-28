from flask import Blueprint

# Crear el blueprint de objetos
objetos_bp = Blueprint("objetos", __name__)


@objetos_bp.route("/")
def listar_objetos():
    return "Lista de objetos para rentar"


@objetos_bp.route("/<int:id>")
def ver_objeto(id):
    return f"Viendo objeto {id}"
