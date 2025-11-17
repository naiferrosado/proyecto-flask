from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class PagoForm(FlaskForm):
    metodo = SelectField(
        "Método de Pago",
        choices=[
            ("", "Seleccione un método..."),
            ("Crédito", "Tarjeta de Crédito"),
            ("Débito", "Tarjeta de Débito"),
            ("PayPal", "PayPal"),
        ],
        validators=[DataRequired(message="Debe seleccionar un método de pago.")],
    )

    submit = SubmitField("Pagar Ahora")
