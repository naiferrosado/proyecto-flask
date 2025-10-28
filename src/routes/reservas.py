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
    # Mostrar reservas del usuario actual
    reservas = Reserva.query.filter_by(id_usuario=current_user.id_usuario).all()
    return render_template("reservas/listar.html", reservas=reservas)


@reservas_bp.route("/nueva/<int:id_objeto>", methods=["GET", "POST"])
@login_required
def crear_reserva(id_objeto):
    objeto = Objeto.query.get_or_404(id_objeto)
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

        flash("Reserva creada exitosamente", "success")
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

    # Liberar el objeto
    objeto = Objeto.query.get(reserva.id_objeto)
    objeto.estado = "Disponible"

    # Cambiar estado de la reserva
    reserva.estado = "Cancelada"

    db.session.commit()
    flash("Reserva cancelada exitosamente", "success")
    return redirect(url_for("reservas.listar_reservas"))
