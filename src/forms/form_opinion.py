from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class OpinionForm(FlaskForm):
    comentario = TextAreaField("Comentario", validators=[
        Length(max=255, message="El comentario no puede tener más de 255 caracteres.")
    ])
    calificacion = SelectField("Calificación", choices=[
        (1, "⭐"),
        (2, "⭐⭐"),
        (3, "⭐⭐⭐"),
        (4, "⭐⭐⭐⭐"),
        (5, "⭐⭐⭐⭐⭐")
    ], coerce=int, validators=[
        DataRequired(message="Debe seleccionar una calificación.")
    ])
    fecha = DateField("Fecha", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha es obligatoria.")
    ])
    id_usuario = IntegerField("ID Usuario", validators=[
        DataRequired(message="El ID del usuario es obligatorio.")
    ])
    id_objeto = IntegerField("ID Objeto", validators=[
        DataRequired(message="El ID del objeto es obligatorio.")
    ])
    submit = SubmitField("Guardar")
