# src/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from sqlalchemy import or_, func
from models.usuario import Usuario
from models.objeto import Objeto
from models.categoria import Categoria
from models.incidencia import Incidencia
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from datetime import datetime, date, timedelta

admin_bp = Blueprint("admin", __name__)


# ------------------- MIDDLEWARE -------------------
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, "id_rol", None) != 1:
            flash("No tienes permisos para acceder a esta sección", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# ------------------- DASHBOARD -------------------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "total_categorias": Categoria.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "ingresos_hoy": 0,
        "nuevos_usuarios_hoy": Usuario.query.filter(Usuario.fecha_registro == date.today()).count(),
        "nuevos_objetos_hoy": Objeto.query.filter(Objeto.fecha_publicacion == date.today()).count(),
        "reservas_hoy": Reserva.query.filter(Reserva.fecha_reserva == date.today()).count(),
    }

    actividad_reciente = [
        {
            "titulo": "Nuevo usuario registrado",
            "descripcion": "Usuario se registró en la plataforma",
            "fecha": datetime.now(),
            "tipo": "info",
        }
    ]

    usuarios_recientes = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(5).all()
    objetos_recientes = Objeto.query.order_by(Objeto.fecha_publicacion.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        actividad_reciente=actividad_reciente,
        usuarios_recientes=usuarios_recientes,
        objetos_recientes=objetos_recientes,
        now=datetime.now(),
    )


# ------------------- USUARIOS -------------------
@admin_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    rol = request.args.get("rol", "", type=str)
    estado = request.args.get("estado", "", type=str)

    query = Usuario.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Usuario.nombre.ilike(like)) |
            (Usuario.apellido.ilike(like)) |
            (Usuario.correo.ilike(like))
        )

    if rol:
        query = query.filter(Usuario.id_rol == int(rol))

    if estado:
        query = query.filter(Usuario.estado == estado)

    usuarios_paginados = query.order_by(Usuario.fecha_registro.desc()).paginate(page=page, per_page=10)

    return render_template("admin/usuarios.html", usuarios=usuarios_paginados)


@admin_bp.route("/usuarios/<int:id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id_rol == 1:
        flash("No se puede eliminar a un administrador.", "error")
        return redirect(url_for("admin.usuarios"))

    db.session.delete(usuario)
    db.session.commit()

    flash(f"Usuario {usuario.nombre} eliminado correctamente.", "success")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<int:id>")
@login_required
@admin_required
def ver_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template("admin/ver_usuario.html", usuario=usuario)


@admin_bp.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        usuario.nombre = request.form.get("nombre")
        usuario.apellido = request.form.get("apellido")
        usuario.correo = request.form.get("correo")
        usuario.telefono = request.form.get("telefono")
        id_rol = request.form.get("id_rol")
        usuario.id_rol = int(id_rol) if id_rol else usuario.id_rol
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for("admin.usuarios"))

    return render_template("admin/editar_usuario.html", usuario=usuario)


# ------------------- CATEGORIAS -------------------
@admin_bp.route("/categorias")
@login_required
@admin_required
def categorias():
    categorias = Categoria.query.all()
    total_objetos = Objeto.query.count()

    categoria_mas_popular = None
    max_objetos = 0
    for categoria in categorias:
        cantidad = len(categoria.objetos)
        if cantidad > max_objetos:
            categoria_mas_popular = categoria
            max_objetos = cantidad

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

    if Categoria.query.filter_by(nombre=nombre).first():
        flash("Ya existe una categoría con ese nombre", "error")
        return redirect(url_for("admin.categorias"))

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
        flash("El nombre es requerido", "error")
        return redirect(url_for("admin.categorias"))

    existe = Categoria.query.filter(Categoria.nombre == nombre, Categoria.id_categoria != categoria_id).first()
    if existe:
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

    if categoria.objetos:
        flash("No se puede eliminar una categoría con objetos.", "error")
        return redirect(url_for("admin.categorias"))

    db.session.delete(categoria)
    db.session.commit()

    flash("Categoría eliminada correctamente", "success")
    return redirect(url_for("admin.categorias"))


# ------------------- INCIDENCIAS -------------------
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

    return render_template("admin/incidencias.html", incidencias=incidencias, incidencias_pendientes=incidencias_pendientes)


@admin_bp.route("/incidencias/<int:id>/actualizar", methods=["POST"])
@login_required
@admin_required
def actualizar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)
    nuevo_estado = request.form.get("nuevo_estado")
    if nuevo_estado not in ["Abierta", "En Proceso", "Resuelta"]:
        flash("Estado no válido", "error")
        return redirect(url_for("admin.incidencias"))
    incidencia.estado = nuevo_estado
    db.session.commit()
    flash("Incidencia actualizada correctamente", "success")
    return redirect(url_for("admin.incidencias"))


# ------------------- REPORTES -------------------
@admin_bp.route("/reportes")
@login_required
@admin_required
def reportes():
    # Leer parámetros GET (si vienen)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    tipo_reporte = request.args.get("tipo", "general")

    # Fechas por defecto (últimos 30 días)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)

    # Parsear fechas si vienen en query
    try:
        if start_date_str:
            fecha_inicio = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            fecha_fin = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        flash("Formato de fecha inválido. Se usarán las fechas por defecto.", "error")
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=30)

    # Asegurar orden correcto (inicio <= fin)
    if fecha_inicio > fecha_fin:
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    # -- Estadísticas básicas (filtradas) --
    ingresos_totales = (
        db.session.query(func.coalesce(func.sum(Pago.monto), 0))
        .join(Reserva, Pago.id_reserva == Reserva.id_reserva)
        .filter(Pago.fecha_pago.between(fecha_inicio, fecha_fin))
        .scalar() or 0
    )

    reservas_completadas = (
        Reserva.query.filter(
            Reserva.estado == "Finalizada",
            Reserva.fecha_reserva.between(fecha_inicio, fecha_fin)
        ).count()
    )

    nuevos_usuarios = Usuario.query.filter(
        Usuario.fecha_registro.between(fecha_inicio, fecha_fin)
    ).count()

    objetos_publicados = Objeto.query.filter(
        Objeto.fecha_publicacion.between(fecha_inicio, fecha_fin)
    ).count()

    estadisticas = {
        "ingresos_totales": float(ingresos_totales),
        "reservas_completadas": int(reservas_completadas),
        "nuevos_usuarios": int(nuevos_usuarios),
        "objetos_publicados": int(objetos_publicados),
    }

    # -- Top propietarios: por ingresos en el rango --
    top_prop_q = (
        db.session.query(
            Usuario,
            func.coalesce(func.sum(Pago.monto), 0).label("total_ingresos"),
            func.count(Reserva.id_reserva).label("total_reservas")
        )
        .join(Objeto, Usuario.id_usuario == Objeto.id_usuario)
        .join(Reserva, Reserva.id_objeto == Objeto.id_objeto)
        .join(Pago, Pago.id_reserva == Reserva.id_reserva)
        .filter(Pago.fecha_pago.between(fecha_inicio, fecha_fin))
        .group_by(Usuario.id_usuario)
        .order_by(func.sum(Pago.monto).desc())
        .limit(5)
        .all()
    )

    top_propietarios = []
    for usuario, ingresos, reservas_totales in top_prop_q:
        top_propietarios.append({
            "nombre": f"{usuario.nombre} {usuario.apellido}",
            "objetos": len(usuario.objetos),
            "ingresos": float(ingresos or 0),
            "reservas": int(reservas_totales or 0),
        })

    # -- Objetos populares: reservas (rango) y promedio de calificación --
    # Subconsulta reservas por objeto en rango
    res_sub = (
        db.session.query(
            Reserva.id_objeto.label("id_objeto"),
            func.count(Reserva.id_reserva).label("cnt_reservas")
        )
        .filter(Reserva.fecha_reserva.between(fecha_inicio, fecha_fin))
        .group_by(Reserva.id_objeto)
        .subquery()
    )

    # Subconsulta promedio calificaciones (puede no tener rango)
    opin_sub = (
        db.session.query(
            Opinion.id_objeto.label("id_objeto"),
            func.avg(Opinion.calificacion).label("avg_calif")
        )
        .group_by(Opinion.id_objeto)
        .subquery()
    )

    objs_pop_q = (
        db.session.query(
            Objeto,
            func.coalesce(res_sub.c.cnt_reservas, 0).label("total_reservas"),
            func.coalesce(opin_sub.c.avg_calif, 0).label("promedio_calificacion")
        )
        .outerjoin(res_sub, Objeto.id_objeto == res_sub.c.id_objeto)
        .outerjoin(opin_sub, Objeto.id_objeto == opin_sub.c.id_objeto)
        .order_by(func.coalesce(res_sub.c.cnt_reservas, 0).desc(), func.coalesce(opin_sub.c.avg_calif, 0).desc())
        .limit(10)
        .all()
    )

    objetos_populares = []
    for objeto, total_reservas, promedio_calificacion in objs_pop_q:
        objetos_populares.append({
            "nombre": objeto.nombre,
            "reservas": int(total_reservas or 0),
            "calificacion": float(promedio_calificacion or 0),
        })

    # -- Tendencias (básico) --
    # porcentaje cambio reservas (vs periodo anterior)
    rango_days = (fecha_fin - fecha_inicio).days or 1
    previo_inicio = fecha_inicio - timedelta(days=rango_days + 1)
    previo_fin = fecha_inicio - timedelta(days=1)

    reservas_actual = Reserva.query.filter(Reserva.fecha_reserva.between(fecha_inicio, fecha_fin)).count()
    reservas_prev = Reserva.query.filter(Reserva.fecha_reserva.between(previo_inicio, previo_fin)).count()
    reservas_pct = round(((reservas_actual - reservas_prev) / reservas_prev * 100) if reservas_prev > 0 else 0, 2)

    usuarios_actual = Usuario.query.filter(Usuario.fecha_registro.between(fecha_inicio, fecha_fin)).count()
    usuarios_prev = Usuario.query.filter(Usuario.fecha_registro.between(previo_inicio, previo_fin)).count()
    usuarios_pct = round(((usuarios_actual - usuarios_prev) / usuarios_prev * 100) if usuarios_prev > 0 else 0, 2)

    # categorías: comparar cantidad de objetos publicados en el periodo vs anterior
    cats = (
        db.session.query(
            Categoria.id_categoria,
            Categoria.nombre,
            func.count(Objeto.id_objeto).label("cnt")
        )
        .outerjoin(Objeto, Categoria.id_categoria == Objeto.id_categoria)
        .filter(Objeto.fecha_publicacion.between(fecha_inicio, fecha_fin))
        .group_by(Categoria.id_categoria, Categoria.nombre)
        .all()
    )

    # Para simplicidad si no hay datos mostramos placeholders
    cat_positiva = {"nombre": "N/A", "porcentaje": 0}
    cat_negativa = {"nombre": "N/A", "porcentaje": 0}
    if cats:
        # Convert to list sorted by cnt
        cats_sorted = sorted(cats, key=lambda x: x.cnt, reverse=True)
        cat_positiva["nombre"] = cats_sorted[0].nombre
        cat_positiva["porcentaje"] = int(cats_sorted[0].cnt)
        cat_negativa["nombre"] = cats_sorted[-1].nombre
        cat_negativa["porcentaje"] = int(cats_sorted[-1].cnt)

    tendencias = {
        # kept multiple key names to be flexible con distintos templates
        "reservas": reservas_pct,
        "usuarios": usuarios_pct,
        "crecimiento_reservas": reservas_pct,
        "crecimiento_usuarios": usuarios_pct,
        "cat_positiva": cat_positiva,
        "cat_negativa": cat_negativa,
        "categoria_mayor_alza": cat_positiva,
        "categoria_mayor_baja": cat_negativa,
    }

    return render_template(
        "admin/reportes.html",
        estadisticas=estadisticas,
        top_propietarios=top_propietarios,
        objetos_populares=objetos_populares,
        tendencias=tendencias,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_reporte=tipo_reporte,
    )


# ------------------- EXPORTACIÓN -------------------
@admin_bp.route("/reportes/exportar/<string:formato>")
@login_required
@admin_required
def exportar_reporte(formato):
    if formato not in ["pdf", "excel", "csv"]:
        flash("Formato de exportación no válido.", "error")
        return redirect(url_for("admin.reportes"))

    # Aquí pondrías la lógica de generación (weasyprint / pandas / csv)
    return f"Generando {formato.upper()}..."


# ------------------- CONFIGURACIÓN -------------------
@admin_bp.route("/configuracion")
@login_required
@admin_required
def configuracion():
    return render_template("admin/configuracion.html")


@admin_bp.route("/configuracion/guardar", methods=["POST"])
@login_required
@admin_required
def guardar_configuracion():
    flash("Configuración guardada correctamente", "success")
    return redirect(url_for("admin.configuracion"))


# ------------------- API LIVE STATS -------------------
@admin_bp.route("/api/estadisticas")
@login_required
@admin_required
def api_estadisticas():
    stats = {
        "total_usuarios": Usuario.query.count(),
        "total_objetos": Objeto.query.count(),
        "total_reservas": Reserva.query.count(),
        "incidencias_pendientes": Incidencia.query.filter_by(estado="Abierta").count(),
        "nuevos_usuarios_hoy": Usuario.query.filter(Usuario.fecha_registro == date.today()).count()
    }
    return jsonify(stats)
