from flask import Flask
from extensions import db, migrate  # Importamos desde extensions
from models import usuario, rol, reserva, pago, opinion, objeto, incidencia, categoria

app = Flask(__name__)

USER_DB = "postgres"
USER_PASSWORD = "postgres"
SERVER_DB = "localhost"
NAME_DB = "Rentflow"
FULL_URL_DB = f"postgresql://{USER_DB}:{USER_PASSWORD}@{SERVER_DB}/{NAME_DB}"

app.config["SQLALCHEMY_DATABASE_URI"] = FULL_URL_DB
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializamos las extensiones con la app
db.init_app(app)
migrate.init_app(app, db)


if __name__ == "__main__":
    app.run(debug=True)
