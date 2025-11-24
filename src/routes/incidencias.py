from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.incidencia import Incidencia
from models.reserva import Reserva
from src.forms.form_incidencias import IncidenciaForm
from datetime import date

incidencias_bp = Blueprint("incidencias", __name__)


@incidencias_bp.route("/")
@login_required
def listar_incidencias():
    # Obtener filtros del query string
    estado = request.args.get("estado", "todas")
    orden = request.args.get("orden", "desc")

    query = Incidencia.query

    # Filtrar por estado
    if estado == "pendiente":
        query = query.filter(Incidencia.estado == "Abierta")
    elif estado == "proceso":
        query = query.filter(Incidencia.estado == "En Proceso")
    elif estado == "resuelta":
        query = query.filter(Incidencia.estado == "Resuelta")
    # "todas" no filtra nada

    # Si NO es admin → solo ve sus incidencias
    if current_user.id_rol != 1:
        query = query.filter_by(id_usuario=current_user.id_usuario)

    # Ordenar por fecha
    if orden == "asc":
        query = query.order_by(Incidencia.fecha_reporte.asc())
    else:
        query = query.order_by(Incidencia.fecha_reporte.desc())

    print(f"Filtro estado: {estado}, orden: {orden}, user: {current_user.id_usuario}")
    print(f"Total incidencias encontradas: {query.count()}")

    incidencias = query.all()

    return render_template("incidencias/listar.html", incidencias=incidencias)



@incidencias_bp.route("/crear/<int:id_reserva>", methods=["GET", "POST"])
@login_required
def crear_incidencia(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    if request.method == "POST":
        descripcion = request.form.get("descripcion", "")
        descripcion = descripcion[:255]  # Limitar a 255 caracteres

        nueva = Incidencia(
            descripcion=descripcion,
            fecha_reporte=date.today(),
            id_usuario=current_user.id_usuario,
            id_reserva=id_reserva
        )

        db.session.add(nueva)
        db.session.commit()

        flash("Incidencia reportada correctamente.", "success")
        return redirect(url_for("reservas.detalle", id=id_reserva))

    return render_template("incidencias/crear.html", reserva=reserva)


@incidencias_bp.route("/<int:id>/actualizar", methods=["POST"])
@login_required
def actualizar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)

    # Solo administradores pueden actualizar incidencias
    if current_user.id_rol != 1:
        flash("Solo los administradores pueden actualizar incidencias", "error")
        return redirect(url_for("incidencias.listar_incidencias"))

    nuevo_estado = request.form.get("nuevo_estado")
    if nuevo_estado in ["Abierta", "En Proceso", "Resuelta"]:
        incidencia.estado = nuevo_estado
        db.session.commit()
        flash("Incidencia actualizada exitosamente", "success")
    else:
        flash("Estado no válido", "error")

    return redirect(url_for("incidencias.listar_incidencias"))