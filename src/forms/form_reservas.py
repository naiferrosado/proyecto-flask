from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired

class ReservaForm(FlaskForm):
    fecha_reserva = DateField("Fecha de Reserva", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha de reserva es obligatoria.")
    ])
    fecha_inicio = DateField("Fecha de Inicio", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha de inicio es obligatoria.")
    ])
    fecha_fin = DateField("Fecha de Fin", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha de fin es obligatoria.")
    ])
    estado = SelectField("Estado", choices=[
        ("Pendiente", "Pendiente"),
        ("Confirmada", "Confirmada"),
        ("Cancelada", "Cancelada"),
        ("Finalizada", "Finalizada")
    ], validators=[DataRequired(message="Debe seleccionar un estado.")])
    id_usuario = IntegerField("ID Usuario", validators=[
        DataRequired(message="El ID del usuario es obligatorio.")
    ])
    id_objeto = IntegerField("ID Objeto", validators=[
        DataRequired(message="El ID del objeto es obligatorio.")
    ])
    submit = SubmitField("Guardar")
