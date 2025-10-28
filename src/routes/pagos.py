from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.pago import Pago
from models.reserva import Reserva
from src.forms.form_pagos import PagoForm
from datetime import date

pagos_bp = Blueprint("pagos", __name__)


@pagos_bp.route("/procesar/<int:id_reserva>", methods=["GET", "POST"])
@login_required
def procesar_pago(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    # Verificar que la reserva pertenezca al usuario
    if reserva.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para pagar esta reserva", "error")
        return redirect(url_for("reservas.listar_reservas"))

    form = PagoForm()

    if form.validate_on_submit():
        # Calcular el monto basado en los días de reserva
        dias = (reserva.fecha_fin - reserva.fecha_inicio).days
        monto_total = dias * reserva.objeto.precio

        pago = Pago(
            monto=monto_total,
            fecha_pago=date.today(),
            metodo=form.metodo.data,
            estado="Completado",
            id_reserva=id_reserva,
        )

        # Actualizar estado de la reserva
        reserva.estado = "Confirmada"

        db.session.add(pago)
        db.session.commit()

        flash("Pago procesado exitosamente", "success")
        return redirect(url_for("reservas.listar_reservas"))

    # Calcular monto para mostrar en el template
    dias = (reserva.fecha_fin - reserva.fecha_inicio).days
    monto_total = dias * reserva.objeto.precio

    return render_template(
        "pagos/procesar.html", form=form, reserva=reserva, monto_total=monto_total
    )


@pagos_bp.route("/historial")
@login_required
def historial_pagos():
    # Obtener pagos de las reservas del usuario
    pagos = (
        Pago.query.join(Reserva)
        .filter(Reserva.id_usuario == current_user.id_usuario)
        .all()
    )

    return render_template("pagos/historial.html", pagos=pagos)
