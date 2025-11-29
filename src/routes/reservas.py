from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.reserva import Reserva
from models.objeto import Objeto
from src.forms.form_reservas import ReservaForm
from datetime import date

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/")
@login_required
def listar_reservas():
    if current_user.id_rol in [1, 3]:
        flash("Los administradores y propietarios no tienen acceso a esta sección.", "danger")
        return redirect(url_for("main.index"))
    
    # Mostrar reservas del usuario actual
    reservas = Reserva.query.filter_by(id_usuario=current_user.id_usuario).all()
    return render_template("reservas/listar.html", reservas=reservas)


@reservas_bp.route("/nueva/<int:id_objeto>", methods=["GET", "POST"])
@login_required
def crear_reserva(id_objeto):
    objeto = Objeto.query.get_or_404(id_objeto)
    
    # Restricción: Los propietarios no pueden reservar
    if current_user.rol.nombre == 'Propietario':
        flash("Los propietarios no pueden realizar reservas.", "error")
        return redirect(url_for("objetos.detalle_objeto", id_objeto=id_objeto))

    form = ReservaForm()

    if form.validate_on_submit():
        # Verificar que el objeto esté disponible
        if objeto.estado != "Disponible":
            flash("Este objeto no está disponible para reservar", "error")
            return redirect(url_for("objetos.detalle_objeto", id=id_objeto))

        # Verificar que las fechas sean válidas
        if form.fecha_inicio.data >= form.fecha_fin.data:
            flash("La fecha de inicio debe ser anterior a la fecha de fin", "error")
            return render_template("reservas/crear.html", form=form, objeto=objeto)

        # Verificar que la fecha de inicio sea futura
        if form.fecha_inicio.data < date.today():
            flash("La fecha de inicio debe ser hoy o posterior", "error")
            return render_template("reservas/crear.html", form=form, objeto=objeto)

        reserva = Reserva(
            fecha_reserva=date.today(),
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            estado="Pendiente",
            id_usuario=current_user.id_usuario,
            id_objeto=id_objeto,
        )

        # Cambiar estado del objeto a Reservado
        objeto.estado = "Reservado"

        db.session.add(reserva)
        db.session.commit()

        flash("¡Reserva creada exitosamente! Ahora procede con el pago.", "success")
        return redirect(url_for("reservas.listar_reservas"))

    return render_template("reservas/crear.html", form=form, objeto=objeto)


@reservas_bp.route("/<int:id>/cancelar")
@login_required
def cancelar_reserva(id):
    reserva = Reserva.query.get_or_404(id)

    # Verificar que el usuario sea el dueño de la reserva
    if reserva.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para cancelar esta reserva", "error")
        return redirect(url_for("reservas.listar_reservas"))

    # Solo se pueden cancelar reservas Pendientes o Activas
    if reserva.estado not in ["Pendiente", "Activa"]:
        flash("Solo puedes cancelar reservas pendientes o activas", "warning")
        return redirect(url_for("reservas.listar_reservas"))

    # Liberar el objeto
    objeto = Objeto.query.get(reserva.id_objeto)
    objeto.estado = "Disponible"

    # Cambiar estado de la reserva
    reserva.estado = "Cancelada"

    db.session.commit()
    flash("Reserva cancelada exitosamente", "success")
    return redirect(url_for("reservas.listar_reservas"))


@reservas_bp.route("/detalle/<int:id>")
@login_required
def detalle(id):
    reserva = Reserva.query.get_or_404(id)

    # Validar si pertenece al usuario
    if reserva.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para ver esta reserva", "error")
        return redirect(url_for("reservas.listar_reservas"))

    objeto = Objeto.query.get(reserva.id_objeto)

    return render_template("reservas/detalle.html", reserva=reserva, objeto=objeto)
