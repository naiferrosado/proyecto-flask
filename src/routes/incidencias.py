from flask import Blueprint, render_template, redirect, url_for, flash
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
    if current_user.id_rol == 1:  # Administrador
        incidencias = Incidencia.query.all()
    else:
        incidencias = Incidencia.query.filter_by(
            id_usuario=current_user.id_usuario
        ).all()

    return render_template("incidencias/listar.html", incidencias=incidencias)


@incidencias_bp.route("/nueva/<int:id_reserva>", methods=["GET", "POST"])
@login_required
def crear_incidencia(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    # Verificar que la reserva pertenezca al usuario
    if reserva.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para reportar incidencias en esta reserva", "error")
        return redirect(url_for("reservas.listar_reservas"))

    form = IncidenciaForm()

    if form.validate_on_submit():
        incidencia = Incidencia(
            descripcion=form.descripcion.data,
            estado="Abierta",
            fecha_reporte=date.today(),
            id_usuario=current_user.id_usuario,
            id_reserva=id_reserva,
        )

        db.session.add(incidencia)
        db.session.commit()

        flash("Incidencia reportada exitosamente", "success")
        return redirect(url_for("incidencias.listar_incidencias"))

    return render_template("incidencias/crear.html", form=form, reserva=reserva)


@incidencias_bp.route("/<int:id>/actualizar", methods=["GET", "POST"])
@login_required
def actualizar_incidencia(id):
    incidencia = Incidencia.query.get_or_404(id)

    # Solo administradores pueden actualizar incidencias
    if current_user.id_rol != 1:
        flash("Solo los administradores pueden actualizar incidencias", "error")
        return redirect(url_for("incidencias.listar_incidencias"))

    form = IncidenciaForm(obj=incidencia)

    if form.validate_on_submit():
        incidencia.estado = form.estado.data
        incidencia.descripcion = form.descripcion.data

        db.session.commit()
        flash("Incidencia actualizada exitosamente", "success")
        return redirect(url_for("incidencias.listar_incidencias"))

    return render_template("incidencias/editar.html", form=form, incidencia=incidencia)
