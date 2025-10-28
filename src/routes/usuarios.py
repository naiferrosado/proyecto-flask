from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.usuario import Usuario
from src.forms.form_usuarios import UsuarioForm
from werkzeug.security import generate_password_hash

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/perfil")
@login_required
def perfil():
    return render_template("usuarios/perfil.html", usuario=current_user)


@usuarios_bp.route("/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = UsuarioForm(obj=current_user)

    # Remover validación de contraseña para edición
    form.contrasena.validators = []
    form.contrasena.description = "Dejar en blanco para mantener la contraseña actual"

    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.correo = form.correo.data
        current_user.telefono = form.telefono.data
        current_user.direccion = form.direccion.data

        # Actualizar contraseña solo si se proporciona una nueva
        if form.contrasena.data:
            current_user.set_password(form.contrasena.data)

        db.session.commit()
        flash("Perfil actualizado exitosamente", "success")
        return redirect(url_for("usuarios.perfil"))

    return render_template("usuarios/editar.html", form=form)
