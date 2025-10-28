from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RolForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
        DataRequired(message="El nombre del rol es obligatorio."),
        Length(max=50, message="El nombre no puede superar los 50 caracteres.")
    ])
    descripcion = TextAreaField("Descripción", validators=[
        Length(max=100, message="La descripción no puede superar los 100 caracteres.")
    ])
    submit = SubmitField("Guardar")