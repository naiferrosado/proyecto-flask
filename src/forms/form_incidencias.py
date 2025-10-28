from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length

class IncidenciaForm(FlaskForm):
    descripcion = TextAreaField("Descripción", validators=[
        DataRequired(message="La descripción es obligatoria."),
        Length(max=255, message="La descripción no puede tener más de 255 caracteres.")
    ])
    estado = SelectField("Estado", choices=[
        ("Abierta", "Abierta"),
        ("En Proceso", "En Proceso"),
        ("Cerrada", "Cerrada")
    ], validators=[DataRequired(message="Debe seleccionar un estado.")])
    fecha_reporte = DateField("Fecha de Reporte", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha de reporte es obligatoria.")
    ])
    id_usuario = IntegerField("ID Usuario", validators=[DataRequired(message="El ID del usuario es obligatorio.")])
    id_reserva = IntegerField("ID Reserva", validators=[DataRequired(message="El ID de la reserva es obligatorio.")])
    submit = SubmitField("Guardar")
