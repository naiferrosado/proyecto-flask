from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime

# Importar modelos
from models.usuario import Usuario
from models.rol import Rol
from models.categoria import Categoria
from models.objeto import Objeto
from models.incidencia import Incidencia
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion


# =============================================
# CONFIGURACIÓN DEL BLUEPRINT
# =============================================
admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


# =============================================
# DECORADOR DE AUTORIZACIÓN
# =============================================
def admin_required(f):
    """Restringe acceso solo a usuarios con rol de administrador."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(
                "Debes iniciar sesión para acceder al panel de administración.",
                "warning",
            )
            return redirect(url_for("auth.login"))
        if current_user.id_rol != 1:
            flash(
                "No tienes permisos para acceder al panel de administración.", "danger"
            )
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


# =============================================
# PANEL PRINCIPAL DEL ADMINISTRADOR
# =============================================
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_usuarios = Usuario.query.count()
    total_objetos = Objeto.query.count()
    total_reservas = Reserva.query.count()
    total_incidencias = Incidencia.query.count()

    recientes = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(5).all()

    return render_template(
        "admin/panel_admin.html",
        total_usuarios=total_usuarios,
        total_objetos=total_objetos,
        total_reservas=total_reservas,
        total_incidencias=total_incidencias,
        recientes=recientes,
    )


# =============================================
# GESTIÓN DE USUARIOS
# =============================================
@admin_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    page = request.args.get("page", 1, type=int)
    usuarios = Usuario.query.order_by(Usuario.id_usuario.asc()).paginate(
        page=page, per_page=10
    )
    return render_template("admin/usuarios.html", usuarios=usuarios)


# =============================================
# GESTIÓN DE CATEGORÍAS
# =============================================
@admin_bp.route("/categorias")
@login_required
@admin_required
def categorias():
    categorias = Categoria.query.all()
    return render_template("admin/categorias.html", categorias=categorias)


@admin_bp.route("/categorias/agregar", methods=["POST"])
@login_required
@admin_required
def agregar_categoria():
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")

    if not nombre:
        flash("El nombre de la categoría es obligatorio.", "warning")
        return redirect(url_for("admin.categorias"))

    categoria = Categoria(nombre=nombre, descripcion=descripcion)
    db.session.add(categoria)
    db.session.commit()
    flash("Categoría agregada correctamente.", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/eliminar/<int:id_categoria>", methods=["POST"])
@login_required
@admin_required
def eliminar_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada correctamente.", "success")
    return redirect(url_for("admin.categorias"))


# =============================================
# GESTIÓN DE INCIDENCIAS
# =============================================
@admin_bp.route("/incidencias")
@login_required
@admin_required
def incidencias():
    incidencias = (
        Incidencia.query.order_by(Incidencia.fecha_reporte.desc())
        .join(Usuario)
        .add_columns(
            Incidencia.id_incidencia,
            Incidencia.descripcion,
            Incidencia.estado,
            Incidencia.fecha_reporte,
            Usuario.nombre.label("nombre_usuario"),
        )
        .all()
    )
    return render_template("admin/incidencias.html", incidencias=incidencias)


# =============================================
# CONFIGURACIÓN DEL ADMINISTRADOR
# =============================================
@admin_bp.route("/configuracion")
@login_required
@admin_required
def configuracion():
    return render_template("admin/configuracion.html")


# =============================================
# REPORTES Y ESTADÍSTICAS
# =============================================
@admin_bp.route("/reportes")
@login_required
@admin_required
def reportes():
    total_ingresos = db.session.query(db.func.sum(Pago.monto)).scalar() or 0
    reservas_completadas = Reserva.query.filter_by(estado="Completada").count()
    incidencias_abiertas = Incidencia.query.filter_by(estado="Abierta").count()

    return render_template(
        "admin/reportes.html",
        total_ingresos=total_ingresos,
        reservas_completadas=reservas_completadas,
        incidencias_abiertas=incidencias_abiertas,
    )
