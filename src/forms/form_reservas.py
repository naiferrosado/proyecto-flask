from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired


class ReservaForm(FlaskForm):
    """Formulario simplificado para crear reservas"""

    fecha_inicio = DateField(
        "Fecha de Inicio",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha de inicio es obligatoria.")],
    )
    fecha_fin = DateField(
        "Fecha de Fin",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha de fin es obligatoria.")],
    )
    submit = SubmitField("Confirmar Reserva")
