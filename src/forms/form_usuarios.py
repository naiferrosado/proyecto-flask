from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=50, message="El nombre no puede superar los 50 caracteres."),
        ],
    )
    apellido = StringField(
        "Apellido",
        validators=[
            DataRequired(message="El apellido es obligatorio."),
            Length(max=50, message="El apellido no puede superar los 50 caracteres."),
        ],
    )
    correo = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Debe ser un correo válido."),
            Length(max=100, message="El correo no puede superar los 100 caracteres."),
        ],
    )
    contrasena = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(
                min=6,
                max=100,
                message="La contraseña debe tener entre 6 y 100 caracteres.",
            ),
        ],
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(message="El teléfono es obligatorio."),
            Length(max=15, message="El teléfono no puede superar los 15 caracteres."),
        ],
    )
    direccion = StringField(
        "Dirección",
        validators=[
            DataRequired(message="La dirección es obligatoria."),
            Length(
                max=100, message="La dirección no puede superar los 100 caracteres."
            ),
        ],
    )
    fecha_registro = DateField(
        "Fecha de Registro",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha de registro es obligatoria.")],
    )
    id_rol = IntegerField(
        "ID Rol", validators=[DataRequired(message="El ID del rol es obligatorio.")]
    )
    submit = SubmitField("Guardar")


# AGREGAR ESTOS NUEVOS FORMULARIOS:
class LoginForm(FlaskForm):
    correo = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Debe ser un correo válido."),
        ],
    )
    contrasena = PasswordField(
        "Contraseña", validators=[DataRequired(message="La contraseña es obligatoria.")]
    )
    submit = SubmitField("Iniciar Sesión")


class RegistrationForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=50, message="El nombre no puede superar los 50 caracteres."),
        ],
    )
    apellido = StringField(
        "Apellido",
        validators=[
            DataRequired(message="El apellido es obligatorio."),
            Length(max=50, message="El apellido no puede superar los 50 caracteres."),
        ],
    )
    correo = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Debe ser un correo válido."),
            Length(max=100, message="El correo no puede superar los 100 caracteres."),
        ],
    )
    contrasena = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres."),
            EqualTo("confirmar_contrasena", message="Las contraseñas deben coincidir"),
        ],
    )
    confirmar_contrasena = PasswordField(
        "Confirmar Contraseña",
        validators=[DataRequired(message="Debe confirmar la contraseña.")],
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(message="El teléfono es obligatorio."),
            Length(max=15, message="El teléfono no puede superar los 15 caracteres."),
        ],
    )
    direccion = StringField(
        "Dirección",
        validators=[
            DataRequired(message="La dirección es obligatoria."),
            Length(
                max=100, message="La dirección no puede superar los 100 caracteres."
            ),
        ],
    )
    # ELIMINAR el campo id_rol - se asignará automáticamente
    submit = SubmitField("Registrarse")
