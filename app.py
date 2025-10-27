from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

USER_DB = "postgres"
USER_PASSWORD = "postgres"
SERVER_DB = "localhost"
NAME_DB = "Rentflow"
FULL_URL_DB = f"postgresql://{USER_DB}:{USER_PASSWORD}@{SERVER_DB}/{NAME_DB}"

app.config["SQLALCHEMY_DATABASE_URI"] = FULL_URL_DB

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(debug=True)
