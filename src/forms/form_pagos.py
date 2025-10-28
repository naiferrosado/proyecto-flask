from flask_wtf import FlaskForm
from wtforms import DecimalField, DateField, StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class PagoForm(FlaskForm):
    monto = DecimalField("Monto", places=2, validators=[
        DataRequired(message="El monto es obligatorio."),
        NumberRange(min=0, message="El monto debe ser positivo.")
    ])
    fecha_pago = DateField("Fecha de Pago", format="%Y-%m-%d", validators=[
        DataRequired(message="La fecha de pago es obligatoria.")
    ])
    metodo = StringField("Método de Pago", validators=[
        DataRequired(message="El método de pago es obligatorio."),
        Length(max=30, message="El método no puede superar los 30 caracteres.")
    ])
    estado = SelectField("Estado", choices=[
        ("Completado", "Completado 🟢"),
        ("Pendiente", "Pendiente 🟡"),
        ("Cancelado", "Cancelado 🔴")
    ], validators=[DataRequired(message="Debe seleccionar un estado.")])
    id_reserva = IntegerField("ID Reserva", validators=[
        DataRequired(message="El ID de la reserva es obligatorio.")
    ])
    submit = SubmitField("Guardar")