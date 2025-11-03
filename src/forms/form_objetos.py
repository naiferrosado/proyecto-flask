from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired


class ObjetoForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=100, message="El nombre no puede tener más de 100 caracteres."),
        ],
    )
    descripcion = TextAreaField(
        "Descripción",
        validators=[
            Length(
                max=255, message="La descripción no puede tener más de 255 caracteres."
            )
        ],
    )
    estado = SelectField(
        "Estado",
        choices=[
            ("Disponible", "Disponible 🟢"),
            ("Reservado", "Reservado 🟡"),
            ("No Disponible", "No disponible 🔴"),
        ],
        validators=[DataRequired(message="Debe seleccionar un estado.")],
    )

    precio = DecimalField(
        "Precio",
        places=2,
        validators=[
            DataRequired(message="El precio es obligatorio."),
            NumberRange(min=0, message="El precio debe ser un valor positivo."),
        ],
    )

    # ✅ Ahora el campo imagen es un FileField, no una URL
    imagen = FileField(
        "Imagen del Objeto",
        validators=[
            FileRequired(message="Debes subir una imagen."),
            FileAllowed(
                ["jpg", "jpeg", "png", "gif"],
                "Solo se permiten imágenes (JPG, PNG o GIF).",
            ),
        ],
    )

    fecha_publicacion = DateField(
        "Fecha de Publicación",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha de publicación es obligatoria.")],
    )
    id_usuario = IntegerField(
        "ID Usuario",
        validators=[DataRequired(message="El ID del usuario es obligatorio.")],
    )
    id_categoria = IntegerField(
        "ID Categoría",
        validators=[DataRequired(message="El ID de la categoría es obligatorio.")],
    )

    submit = SubmitField("Guardar")
