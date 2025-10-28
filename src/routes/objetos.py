# src/routes/objetos.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.objeto import Objeto
from models.categoria import Categoria
from src.forms.form_objetos import ObjetoForm
from datetime import date

objetos_bp = Blueprint("objetos", __name__)


@objetos_bp.route("/")
def listar_objetos():
    objetos = Objeto.query.filter_by(estado="Disponible").all()
    categorias = Categoria.query.all()
    return render_template(
        "objetos/listar.html", objetos=objetos, categorias=categorias
    )


@objetos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear_objeto():
    form = ObjetoForm()

    # Obtener categorías para el select
    categorias = Categoria.query.all()
    form.id_categoria.choices = [(c.id_categoria, c.nombre) for c in categorias]

    if form.validate_on_submit():
        objeto = Objeto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            estado=form.estado.data,
            imagen=form.imagen.data or "default.jpg",
            fecha_publicacion=date.today(),
            id_usuario=current_user.id_usuario,
            id_categoria=form.id_categoria.data,
        )

        db.session.add(objeto)
        db.session.commit()
        flash("Objeto publicado exitosamente", "success")
        return redirect(url_for("objetos.listar_objetos"))

    return render_template("objetos/crear.html", form=form)


@objetos_bp.route("/<int:id>")
def detalle_objeto(id):
    objeto = Objeto.query.get_or_404(id)
    return render_template("objetos/detalle.html", objeto=objeto)
