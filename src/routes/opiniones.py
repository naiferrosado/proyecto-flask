from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.opinion import Opinion
from models.reserva import Reserva
from src.forms.form_opinion import OpinionForm
from datetime import date

opiniones_bp = Blueprint("opiniones", __name__)


@opiniones_bp.route("/nueva/<int:id_objeto>", methods=["GET", "POST"])
@login_required
def crear_opinion(id_objeto):
    # Verificar que el usuario haya tenido una reserva completada para este objeto
    reserva_completada = Reserva.query.filter_by(
        id_usuario=current_user.id_usuario, id_objeto=id_objeto, estado="Finalizada"
    ).first()

    if not reserva_completada:
        flash(
            "Solo puedes opinar sobre objetos que hayas reservado y finalizado", "error"
        )
        return redirect(url_for("objetos.detalle_objeto", id=id_objeto))

    # Verificar si ya existe una opinión para esta reserva
    opinion_existente = Opinion.query.filter_by(
        id_usuario=current_user.id_usuario, id_objeto=id_objeto
    ).first()

    if opinion_existente:
        flash("Ya has opinado sobre este objeto", "info")
        return redirect(url_for("objetos.detalle_objeto", id=id_objeto))

    form = OpinionForm()

    if form.validate_on_submit():
        opinion = Opinion(
            comentario=form.comentario.data,
            calificacion=form.calificacion.data,
            fecha=date.today(),
            id_usuario=current_user.id_usuario,
            id_objeto=id_objeto,
        )

        db.session.add(opinion)
        db.session.commit()

        flash("Opinión publicada exitosamente", "success")
        return redirect(url_for("objetos.detalle_objeto", id=id_objeto))

    return render_template("opiniones/crear.html", form=form, id_objeto=id_objeto)


@opiniones_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_opinion(id):
    opinion = Opinion.query.get_or_404(id)

    # Verificar que el usuario sea el dueño de la opinión
    if opinion.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para editar esta opinión", "error")
        return redirect(url_for("objetos.detalle_objeto", id=opinion.id_objeto))

    form = OpinionForm(obj=opinion)

    if form.validate_on_submit():
        opinion.comentario = form.comentario.data
        opinion.calificacion = form.calificacion.data
        opinion.fecha = date.today()

        db.session.commit()
        flash("Opinión actualizada exitosamente", "success")
        return redirect(url_for("objetos.detalle_objeto", id=opinion.id_objeto))

    return render_template("opiniones/editar.html", form=form, opinion=opinion)


@opiniones_bp.route("/<int:id>/eliminar")
@login_required
def eliminar_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    id_objeto = opinion.id_objeto

    # Verificar que el usuario sea el dueño de la opinión
    if opinion.id_usuario != current_user.id_usuario:
        flash("No tienes permisos para eliminar esta opinión", "error")
        return redirect(url_for("objetos.detalle_objeto", id=id_objeto))

    db.session.delete(opinion)
    db.session.commit()

    flash("Opinión eliminada exitosamente", "success")
    return redirect(url_for("objetos.detalle_objeto", id=id_objeto))
