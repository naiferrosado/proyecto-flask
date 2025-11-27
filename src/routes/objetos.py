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
from models.imagen_objeto import ImagenObjeto
from src.forms.form_objetos import ObjetoForm
from datetime import date
from models.opinion import Opinion
objetos_bp = Blueprint("objetos", __name__)

# -----------------------------
# Listar objetos publicados
# -----------------------------
@objetos_bp.route("/")
def listar_objetos():
    categoria_id = request.args.get("categoria")
    query = Objeto.query.filter_by(estado="Disponible", publicado=True)

    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)

    objetos = query.all()
    categorias = Categoria.query.all()
    
    return render_template(
        "objetos/listar.html", 
        objetos=objetos, 
        categorias=categorias,
        categoria_seleccionada=categoria_id
    )


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
        nuevo_objeto = Objeto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            id_categoria=form.id_categoria.data,
            precio=form.precio.data,
            id_usuario=current_user.id_usuario,
            estado=form.estado.data,
            publicado=request.form.get("publicar") == "on",
            fecha_publicacion=date.today() if request.form.get("publicar") == "on" else None,
        )
        db.session.add(nuevo_objeto)
        db.session.commit()

        # Guardar imágenes
        imagenes = request.files.getlist("imagenes")
        for img in imagenes[:5]:
            if img:
                filename = secure_filename(img.filename)
                upload_folder = os.path.join(current_app.root_path, "static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)
                img.save(os.path.join(upload_folder, filename))

                nueva_imagen = ImagenObjeto(
                    nombre_archivo=filename,
                    objeto_id=nuevo_objeto.id_objeto
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
# Detalle de objeto (única ruta válida)
# -----------------------------
@objetos_bp.route("/objeto/<int:id_objeto>")
def detalle_objeto(id_objeto):
    objeto = Objeto.query.get_or_404(id_objeto)

    calificaciones = [op.calificacion for op in objeto.opiniones]
    promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

    return render_template(
        "objetos/detalle.html",
        objeto=objeto,
        promedio=promedio
    )


# -----------------------------
# Mis borradores
# -----------------------------
@objetos_bp.route("/borradores")
@login_required
def ver_borradores():
    borradores = Objeto.query.filter_by(
        id_usuario=current_user.id_usuario,
        publicado=False
    ).all()
    return render_template("objetos/mis_borradores.html", objetos=borradores)


# -----------------------------
# Publicar borrador
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
# Eliminar borrador
# -----------------------------
@objetos_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_objeto(id):
    objeto = Objeto.query.get_or_404(id)

    if objeto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para eliminar este objeto.", "danger")
        return redirect(url_for("objetos.ver_borradores"))

    for img in objeto.imagenes:
        try:
            os.remove(
                os.path.join(current_app.root_path, "static/uploads", img.nombre_archivo)
            )
        except FileNotFoundError:
            pass

    db.session.delete(objeto)
    db.session.commit()

    flash("Borrador eliminado correctamente.", "success")
    return redirect(url_for("objetos.ver_borradores"))


# -----------------------------
# Agregar opinión (formulario)
# -----------------------------
@objetos_bp.post("/objeto/<int:id_objeto>/opinion")
@login_required
def agregar_opinion(id_objeto):
    objeto = Objeto.query.get_or_404(id_objeto)

    calificacion = int(request.form["calificacion"])
    comentario = request.form["comentario"]

    nueva_opinion = Opinion(
        id_usuario=current_user.id_usuario,
        id_objeto=id_objeto,
        calificacion=calificacion,
        comentario=comentario,
        fecha=date.today()
    )

    db.session.add(nueva_opinion)
    db.session.commit()

    flash("¡Tu opinión fue guardada correctamente!", "success")
    return redirect(url_for("objetos.detalle_objeto", id_objeto=id_objeto))


# -----------------------------
# Crear opinión (otra versión)
# -----------------------------
@objetos_bp.route("/objeto/<int:id_objeto>/opinar", methods=["POST"])
@login_required
def crear_opinion(id_objeto):
    calificacion = request.form.get("calificacion")
    comentario = request.form.get("comentario")

    if not calificacion or not comentario:
        flash("Debes completar la calificación y el comentario.", "danger")
        return redirect(url_for("objetos.detalle_objeto", id_objeto=id_objeto))

    nueva_opinion = Opinion(
        comentario=comentario,
        calificacion=int(calificacion),
        fecha=date.today(),
        id_usuario=current_user.id_usuario,
        id_objeto=id_objeto
    )

    db.session.add(nueva_opinion)
    db.session.commit()

    flash("Opinión enviada correctamente.", "success")
    return redirect(url_for("objetos.detalle_objeto", id_objeto=id_objeto))