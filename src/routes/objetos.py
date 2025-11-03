import os
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.objeto import Objeto
from models.categoria import Categoria
from src.forms.form_objetos import ObjetoForm
from datetime import date

objetos_bp = Blueprint("objetos", __name__)


@objetos_bp.route("/")
def listar_objetos():
    objetos = Objeto.query.filter_by(estado="Disponible").all()
    return render_template("objetos/listar.html", objetos=objetos)


@objetos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear_objeto():
    form = ObjetoForm()

    # Cargar categorías en el Select
    categorias = Categoria.query.all()
    form.id_categoria.choices = [(c.id_categoria, c.nombre) for c in categorias]

    if form.validate_on_submit():
        # ✅ Guardar la imagen subida
        imagen_file = form.imagen.data
        if imagen_file:
            filename = secure_filename(imagen_file.filename)
            upload_folder = os.path.join(current_app.root_path, "static/uploads")
            os.makedirs(upload_folder, exist_ok=True)  # Crear carpeta si no existe
            imagen_path = os.path.join(upload_folder, filename)
            imagen_file.save(imagen_path)
            # Ruta relativa para guardar en DB
            ruta_imagen = f"uploads/{filename}"
        else:
            ruta_imagen = "uploads/default.jpg"

        # ✅ Crear objeto y guardar en BD
        objeto = Objeto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            estado=form.estado.data,
            imagen=ruta_imagen,
            fecha_publicacion=form.fecha_publicacion.data or date.today(),
            id_usuario=current_user.id_usuario,
            id_categoria=form.id_categoria.data,
        )

        db.session.add(objeto)
        db.session.commit()
        flash("Objeto publicado exitosamente 🟢", "success")
        return redirect(url_for("objetos.listar_objetos"))

    return render_template("objetos/crear.html", form=form)


@objetos_bp.route("/<int:id>")
def detalle_objeto(id):
    objeto = Objeto.query.get_or_404(id)
    return render_template("objetos/detalle.html", objeto=objeto)
