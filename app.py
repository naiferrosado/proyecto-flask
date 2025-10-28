from flask import Flask
from extensions import db, migrate

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://postgres:postgres@localhost/Rentflow"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate.init_app(app, db)

app.config["SECRET_KEY"] = (
    "559f897f7fd39579e84d499305476df7ba8ba8eea89312b282685056b4b8c22b"
)

from models.usuario import Usuario
from models.rol import Rol
from models.reserva import Reserva
from models.pago import Pago
from models.opinion import Opinion
from models.objeto import Objeto
from models.incidencia import Incidencia
from models.categoria import Categoria

if __name__ == "__main__":
    app.run(debug=True)
