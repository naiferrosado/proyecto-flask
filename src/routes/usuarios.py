from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.usuario import Usuario
from src.forms.form_usuarios import UsuarioForm
from src.forms.form_usuarios import EditarPerfilForm
from flask_wtf.csrf import validate_csrf
from werkzeug.security import generate_password_hash

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/perfil")
@login_required
def perfil():
    return render_template("usuarios/perfil.html", usuario=current_user)


@usuarios_bp.route("/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = EditarPerfilForm(obj=current_user)

    if form.validate_on_submit():
        # actualizar campos normales
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.correo = form.correo.data
        current_user.telefono = form.telefono.data
        current_user.direccion = form.direccion.data

        # campos de contraseña enviados por el form
        new_pwd = request.form.get("new_password")
        confirm_pwd = request.form.get("confirm_password")
        # aceptar current_password OR current_password_verified (puesto por JS)
        current_pwd = request.form.get("current_password") or request.form.get("current_password_verified")

        if new_pwd:
            # siempre verificar contraseña actual en servidor
            if not current_user.check_password(current_pwd or ""):
                flash("La contraseña actual no es correcta.", "danger")
                return render_template("usuarios/editar.html", form=form)

            if new_pwd != confirm_pwd:
                flash("La nueva contraseña y su confirmación no coinciden.", "danger")
                return render_template("usuarios/editar.html", form=form)

            if len(new_pwd) < 6:
                flash("La contraseña debe tener al menos 6 caracteres.", "danger")
                return render_template("usuarios/editar.html", form=form)

            # Intentar actualizar usando API del modelo; si no existe, detectar campo y forzar update
            try:
                updated = False
                if hasattr(current_user, "set_password") and callable(current_user.set_password):
                    current_user.set_password(new_pwd)
                    updated = True
                else:
                    # generar hash
                    hashed = generate_password_hash(new_pwd)

                    # detectar automáticamente un campo "password-like" en el modelo
                    pw_field = None
                    try:
                        cols = [c.name for c in Usuario.__table__.columns]
                        for name in cols:
                            lname = name.lower()
                            if "password" in lname or "passwd" in lname or "pass" == lname or "hash" in lname:
                                pw_field = name
                                break
                    except Exception:
                        pw_field = None

                    if pw_field:
                        db.session.query(Usuario).filter_by(id_usuario=current_user.id_usuario).update({pw_field: hashed}, synchronize_session=False)
                        updated = True
                    else:
                        # último recurso: intentar campos comunes en el objeto
                        for field in ("password_hash", "password", "passwd", "hash"):
                            if hasattr(current_user, field):
                                setattr(current_user, field, hashed)
                                updated = True
                                break

                if not updated:
                    raise RuntimeError("No se pudo determinar campo para almacenar la contraseña.")
            except Exception as exc:
                db.session.rollback()
                flash("Error al actualizar la contraseña: " + str(exc), "danger")
                return render_template("usuarios/editar.html", form=form)

        # commit único final (si password fue actualizado vía update ya se aplicó en la sesión/DB)
        try:
            db.session.add(current_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Error al guardar cambios.", "danger")
            return render_template("usuarios/editar.html", form=form)

        flash("Perfil actualizado exitosamente", "success")
        return redirect(url_for("usuarios.perfil"))

    return render_template("usuarios/editar.html", form=form)


@usuarios_bp.route("/verificar_contrasena", methods=["POST"])
@login_required
def verificar_contrasena():
    csrf_token = request.form.get("csrf_token")
    try:
        if csrf_token:
            validate_csrf(csrf_token)
    except Exception:
        return jsonify({"valid": False}), 400

    contrasena = request.form.get("contrasena", "")
    valid = current_user.check_password(contrasena)
    return jsonify({"valid": bool(valid)})

@usuarios_bp.route("/cambiar_rol", methods=["POST"])
@login_required
def cambiar_rol():
    # Evitar que el Admin cambie su rol
    if current_user.id_rol == 1:
        flash("Los administradores no pueden cambiar de rol.", "danger")
        return redirect(url_for("usuarios.mi_perfil"))

    # Alternar entre cliente (2) y propietario (3)
    nuevo_rol = 3 if current_user.id_rol == 2 else 2

    current_user.id_rol = nuevo_rol
    db.session.commit()

    flash("Tu rol ha sido actualizado correctamente.", "success")
    return redirect(url_for("usuarios.perfil"))

