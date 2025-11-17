import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    request,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.objeto import Objeto
from models.categoria import Categoria
from models.imagen_objeto import ImagenObjeto  # Nueva tabla para imágenes
from src.forms.form_objetos import ObjetoForm
from datetime import date
from models.imagen_objeto import ImagenObjeto


objetos_bp = Blueprint("objetos", __name__)


# -----------------------------
# Listar objetos publicados
# -----------------------------
@objetos_bp.route("/")
def listar_objetos():
    objetos = Objeto.query.filter_by(estado="Disponible", publicado=True).all()
    return render_template("objetos/listar.html", objetos=objetos)


# -----------------------------
# Crear nuevo objeto / borrador
# -----------------------------
@objetos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear_objeto():
    form = ObjetoForm()
    categorias = Categoria.query.all()
    form.id_categoria.choices = [(c.id_categoria, c.nombre) for c in categorias]

    if form.validate_on_submit():
        # Crear el objeto
        nuevo_objeto = Objeto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            id_categoria=form.id_categoria.data,
            precio=form.precio.data,
            id_usuario=current_user.id_usuario,
            estado=form.estado.data,
            publicado=request.form.get("publicar") == "on",  # Checkbox para publicar
            fecha_publicacion=date.today()
            if request.form.get("publicar") == "on"
            else None,
        )
        db.session.add(nuevo_objeto)
        db.session.commit()

        # Procesar hasta 5 imágenes
        imagenes = request.files.getlist("imagenes")  # input name="imagenes" multiple
        for img in imagenes[:5]:
            if img:
                filename = secure_filename(img.filename)
                upload_folder = os.path.join(current_app.root_path, "static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)
                img.save(os.path.join(upload_folder, filename))

                nueva_imagen = ImagenObjeto(
                    nombre_archivo=filename, objeto_id=nuevo_objeto.id_objeto
                )
                db.session.add(nueva_imagen)
        db.session.commit()

        flash("Objeto creado correctamente.", "success")
        return redirect(
            url_for("objetos.ver_borradores")
            if not nuevo_objeto.publicado
            else url_for("objetos.listar_objetos")
        )

    return render_template("objetos/crear.html", form=form)


# -----------------------------
# Detalle de objeto
# -----------------------------
@objetos_bp.route("/<int:id>")
def detalle_objeto(id):
    objeto = Objeto.query.get_or_404(id)
    return render_template("objetos/detalle.html", objeto=objeto)


# -----------------------------
# Mis borradores
# -----------------------------
@objetos_bp.route("/borradores")
@login_required
def ver_borradores():
    borradores = Objeto.query.filter_by(
        id_usuario=current_user.id_usuario, publicado=False
    ).all()
    return render_template("objetos/mis_borradores.html", objetos=borradores)


# -----------------------------
# Publicar un borrador
# -----------------------------
@objetos_bp.route("/publicar/<int:id>", methods=["POST"])
@login_required
def publicar_objeto(id):
    objeto = Objeto.query.get_or_404(id)
    if objeto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para publicar este objeto.", "danger")
        return redirect(url_for("objetos.ver_borradores"))

    objeto.publicado = True
    objeto.fecha_publicacion = date.today()
    db.session.commit()
    flash("Objeto publicado correctamente.", "success")
    return redirect(url_for("objetos.listar_objetos"))


# -----------------------------
# Eliminar un borrador
# -----------------------------
@objetos_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_objeto(id):
    objeto = Objeto.query.get_or_404(id)
    if objeto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para eliminar este objeto.", "danger")
        return redirect(url_for("objetos.ver_borradores"))

    # Borrar imágenes del servidor
    for img in objeto.imagenes:
        try:
            os.remove(
                os.path.join(
                    current_app.root_path, "static/uploads", img.nombre_archivo
                )
            )
        except FileNotFoundError:
            pass

    db.session.delete(objeto)
    db.session.commit()
    flash("Borrador eliminado correctamente.", "success")
    return redirect(url_for("objetos.ver_borradores"))
