from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from sqlalchemy import func
from models.usuario import Usuario
from models.objeto import Objeto
from models.categoria import Categoria
from models.incidencia import Incidencia
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from datetime import datetime, date, timedelta

estadisticas_bp = Blueprint("estadisticas", __name__)

# ------------------- MIDDLEWARE -------------------
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, "id_rol", None) != 1:
            flash("No tienes permisos para acceder a esta sección", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function

@estadisticas_bp.route("/")
@login_required
@admin_required
def index():
    # Leer parámetros GET (si vienen)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

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
        "admin/estadisticas.html",
        estadisticas=estadisticas,
        top_propietarios=top_propietarios,
        objetos_populares=objetos_populares,
        tendencias=tendencias,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
