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

    # Validar que la reserva sea del usuario actual
    if reserva.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para pagar esta reserva", "error")
        return redirect(url_for("reservas.listar_reservas"))

    form = PagoForm()

    # Calcular el monto siempre (para mostrarlo)
    dias = (reserva.fecha_fin - reserva.fecha_inicio).days
    monto_total = dias * float(reserva.objeto.precio)

    if form.validate_on_submit():
        pago = Pago(
            monto=monto_total,
            fecha_pago=date.today(),
            metodo=form.metodo.data,
            estado="Completado",
            id_reserva=id_reserva,
        )

        # Cambiar reserva a Confirmada
        reserva.estado = "Confirmada"

        db.session.add(pago)
        db.session.commit()

        flash("Pago procesado exitosamente", "success")
        return redirect(url_for("reservas.listar_reservas"))

    return render_template(
        "pagos/procesar.html", form=form, reserva=reserva, monto_total=monto_total
    )


@pagos_bp.route("/historial")
@login_required
def historial_pagos():
    if current_user.id_rol in [1, 3]:
        flash("Los administradores y propietarios no tienen acceso a esta sección.", "danger")
        return redirect(url_for("main.index"))

    pagos = (
        Pago.query.join(Reserva)
        .filter(Reserva.id_usuario == current_user.id_usuario)
        .all()
    )

    return render_template("pagos/historial.html", pagos=pagos)
