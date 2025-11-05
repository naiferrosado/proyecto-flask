# src/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.usuario import Usuario
from models.objeto import Objeto
from models.categoria import Categoria
from models.incidencia import Incidencia
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from datetime import datetime, date, timedelta

admin_bp = Blueprint("admin", __name__)


# Verificar que el usuario sea administrador
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id_rol != 1:
            flash("No tienes permisos para acceder a esta sección", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Estadísticas para el dashboard
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "total_categorias": Categoria.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "ingresos_hoy": 0,  # Se calcularía con los pagos del día
        "nuevos_usuarios_hoy": Usuario.query.filter(
            Usuario.fecha_registro == date.today()
        ).count(),
        "nuevos_objetos_hoy": Objeto.query.filter(
            Objeto.fecha_publicacion == date.today()
        ).count(),
        "reservas_hoy": Reserva.query.filter(
            Reserva.fecha_reserva == date.today()
        ).count(),
    }

    # Actividad reciente
    actividad_reciente = [
        {
            "titulo": "Nuevo usuario registrado",
            "descripcion": "Usuario se registró en la plataforma",
            "fecha": datetime.now(),
            "tipo": "info",
        }
        # Aquí agregarías más actividades reales de la base de datos
    ]

    # Usuarios recientes
    usuarios_recientes = (
        Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(5).all()
    )

    # Objetos recientes
    objetos_recientes = (
        Objeto.query.order_by(Objeto.fecha_publicacion.desc()).limit(5).all()
    )

    return render_template(
        "dashboard.html",
        stats=stats,
        actividad_reciente=actividad_reciente,
        usuarios_recientes=usuarios_recientes,
        objetos_recientes=objetos_recientes,
        now=datetime.now(),
    )


@admin_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    page = request.args.get("page", 1, type=int)
    usuarios_paginados = Usuario.query.order_by(Usuario.fecha_registro.desc()).paginate(
        page=page, per_page=10
    )

    return render_template("admin/usuarios.html", usuarios=usuarios_paginados)


@admin_bp.route("/usuarios/<int:id>/suspender", methods=["POST"])
@login_required
@admin_required
def suspender_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    # No permitir suspender administradores
    if usuario.id_rol == 1:
        flash("No se puede suspender a un administrador", "error")
        return redirect(url_for("admin.usuarios"))

    # Aquí implementarías la lógica de suspensión
    # Por ejemplo: usuario.activo = False
    flash(f"Usuario {usuario.nombre} suspendido correctamente", "success")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/categorias")
@login_required
@admin_required
def categorias():
    categorias = Categoria.query.all()
    total_objetos = Objeto.query.count()

    # Encontrar categoría más popular
    categoria_mas_popular = None
    max_objetos = 0
    for categoria in categorias:
        if len(categoria.objetos) > max_objetos:
            max_objetos = len(categoria.objetos)
            categoria_mas_popular = categoria

    # Contar categorías sin objetos
    categorias_sin_objetos = sum(1 for c in categorias if len(c.objetos) == 0)

    return render_template(
        "admin/categorias.html",
        categorias=categorias,
        total_objetos=total_objetos,
        categoria_mas_popular=categoria_mas_popular,
        categorias_sin_objetos=categorias_sin_objetos,
    )


@admin_bp.route("/categorias/crear", methods=["POST"])
@login_required
@admin_required
def crear_categoria():
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion", "")

    if not nombre:
        flash("El nombre de la categoría es requerido", "error")
        return redirect(url_for("admin.categorias"))

    # Verificar si ya existe
    categoria_existente = Categoria.query.filter_by(nombre=nombre).first()
    if categoria_existente:
        flash("Ya existe una categoría con ese nombre", "error")
        return redirect(url_for("admin.categorias"))

    # Crear nueva categoría
    nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)

    db.session.add(nueva_categoria)
    db.session.commit()

    flash("Categoría creada correctamente", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/editar", methods=["POST"])
@login_required
@admin_required
def editar_categoria():
    categoria_id = request.form.get("categoria_id")
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion", "")

    categoria = Categoria.query.get_or_404(categoria_id)

    if not nombre:
        flash("El nombre de la categoría es requerido", "error")
        return redirect(url_for("admin.categorias"))

    # Verificar si el nuevo nombre ya existe en otra categoría
    categoria_existente = Categoria.query.filter(
        Categoria.nombre == nombre, Categoria.id_categoria != categoria_id
    ).first()

    if categoria_existente:
        flash("Ya existe otra categoría con ese nombre", "error")
        return redirect(url_for("admin.categorias"))

    categoria.nombre = nombre
    categoria.descripcion = descripcion

    db.session.commit()

    flash("Categoría actualizada correctamente", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    # Verificar que la categoría no tenga objetos
    if categoria.objetos:
        flash("No se puede eliminar una categoría que tiene objetos", "error")
        return redirect(url_for("admin.categorias"))

    db.session.delete(categoria)
    db.session.commit()

    flash("Categoría eliminada correctamente", "success")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/incidencias")
@login_required
@admin_required
def incidencias():
    estado = request.args.get("estado", "")

    query = Incidencia.query

    if estado:
        query = query.filter_by(estado=estado)

    incidencias = query.order_by(Incidencia.fecha_reporte.desc()).all()
    incidencias_pendientes = Incidencia.query.filter_by(estado="Abierta").count()

    return render_template(
        "admin/incidencias.html",
        incidencias=incidencias,
        incidencias_pendientes=incidencias_pendientes,
    )


@admin_bp.route("/incidencias/<int:id>/actualizar", methods=["POST"])
@login_required
@admin_required
def actualizar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)
    nuevo_estado = request.form.get("nuevo_estado")
    comentario = request.form.get("comentario", "")

    if nuevo_estado not in ["Abierta", "En Proceso", "Resuelta"]:
        flash("Estado no válido", "error")
        return redirect(url_for("admin.incidencias"))

    incidencia.estado = nuevo_estado
    if comentario:
        # Aquí podrías agregar el comentario al historial de la incidencia
        pass

    db.session.commit()

    flash("Incidencia actualizada correctamente", "success")
    return redirect(url_for("admin.incidencias"))


@admin_bp.route("/reportes")
@login_required
@admin_required
def reportes():
    # Fechas por defecto (últimos 30 días)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)

    # Estadísticas básicas
    estadisticas = {
        "ingresos_totales": 0,  # Calcularía con los pagos
        "reservas_completadas": Reserva.query.filter_by(estado="Finalizada").count(),
        "nuevos_usuarios": Usuario.query.filter(
            Usuario.fecha_registro.between(fecha_inicio, fecha_fin)
        ).count(),
        "objetos_publicados": Objeto.query.filter(
            Objeto.fecha_publicacion.between(fecha_inicio, fecha_fin)
        ).count(),
    }

    # Top propietarios (podría calcularse con ingresos reales)
    top_propietarios = []
    usuarios_con_objetos = Usuario.query.filter(Usuario.objetos.any()).all()
    for usuario in usuarios_con_objetos[:5]:
        top_propietarios.append(
            {
                "nombre": f"{usuario.nombre} {usuario.apellido}",
                "objetos": len(usuario.objetos),
                "ingresos": 0,  # Calcularía con pagos reales
            }
        )

    # Objetos más populares (podría calcularse con reservas)
    objetos_populares = []
    for objeto in Objeto.query.limit(5).all():
        objetos_populares.append(
            {
                "nombre": objeto.nombre,
                "reservas": len(objeto.reservas),
                "calificacion": 4.5,  # Calcularía promedio de opiniones
            }
        )

    return render_template(
        "admin/reportes.html",
        estadisticas=estadisticas,
        top_propietarios=top_propietarios,
        objetos_populares=objetos_populares,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


@admin_bp.route("/configuracion")
@login_required
@admin_required
def configuracion():
    return render_template("admin/configuracion.html")


@admin_bp.route("/configuracion/guardar", methods=["POST"])
@login_required
@admin_required
def guardar_configuracion():
    # Aquí procesarías la configuración del formulario
    # Por ahora solo un mensaje de éxito
    flash("Configuración guardada correctamente", "success")
    return redirect(url_for("admin.configuracion"))


# API para estadísticas en tiempo real (opcional)
@admin_bp.route("/api/estadisticas")
@login_required
@admin_required
def api_estadisticas():
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "nuevos_usuarios_hoy": Usuario.query.filter(
            Usuario.fecha_registro == date.today()
        ).count(),
    }
    return jsonify(stats)
