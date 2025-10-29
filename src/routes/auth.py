from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.usuario import Usuario
from src.forms.form_usuarios import LoginForm, RegistrationForm
from datetime import date

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(correo=form.correo.data).first()
        if user and user.check_password(form.contrasena.data):
            login_user(user)
            flash("¡Inicio de sesión exitoso!", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Correo o contraseña incorrectos", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Verificar si el correo ya existe
        existing_user = Usuario.query.filter_by(correo=form.correo.data).first()
        if existing_user:
            flash("Este correo ya está registrado", "error")
            return render_template("auth/register.html", form=form)

        # Crear nuevo usuario con rol de Usuario (id_rol=2)
        user = Usuario(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            correo=form.correo.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            fecha_registro=date.today(),
            id_rol=2,  # Rol de Usuario por defecto
        )
        user.set_password(form.contrasena.data)

        db.session.add(user)
        db.session.commit()

        flash(
            "¡Registro exitoso! Ahora puedes publicar objetos y realizar reservas.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("main.index"))
