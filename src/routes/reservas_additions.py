
@reservas_bp.route("/gestionar")
@login_required
def gestionar_reservas():
    if current_user.id_rol != 3:  # Solo propietarios
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("main.index"))

    # Obtener reservas pendientes de los objetos del propietario
    reservas = (
        Reserva.query.join(Objeto)
        .filter(Objeto.id_usuario == current_user.id_usuario)
        .filter(Reserva.estado == "Pendiente")
        .all()
    )
    return render_template("reservas/gestionar.html", reservas=reservas)


@reservas_bp.route("/aprobar/<int:id>")
@login_required
def aprobar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    objeto = Objeto.query.get(reserva.id_objeto)

    if objeto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para aprobar esta reserva.", "error")
        return redirect(url_for("reservas.gestionar_reservas"))

    reserva.estado = "Aceptada"
    db.session.commit()

    flash("Reserva aceptada. El cliente ahora puede proceder al pago.", "success")
    return redirect(url_for("reservas.gestionar_reservas"))


@reservas_bp.route("/rechazar/<int:id>")
@login_required
def rechazar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    objeto = Objeto.query.get(reserva.id_objeto)

    if objeto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para rechazar esta reserva.", "error")
        return redirect(url_for("reservas.gestionar_reservas"))

    reserva.estado = "Rechazada"
    objeto.estado = "Disponible"  # Liberar el objeto
    db.session.commit()

    flash("Reserva rechazada y objeto liberado.", "success")
    return redirect(url_for("reservas.gestionar_reservas"))
