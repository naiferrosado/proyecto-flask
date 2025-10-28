from flask import Blueprint, render_template
from models.objeto import Objeto

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    objetos = Objeto.query.filter_by(estado="Disponible").limit(8).all()
    return render_template("index.html", objetos=objetos)
