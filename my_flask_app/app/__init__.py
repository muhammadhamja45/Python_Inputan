# app/__init__.py
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def generate_secret_key():
    return secrets.token_hex(16)  # Menghasilkan kunci rahasia sepanjang 32 karakter (16 byte)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5433/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = generate_secret_key()  # Setel kunci rahasia menggunakan fungsi pembuat kunci

    db.init_app(app)
    migrate.init_app(app, db)

    from .model import DataSQL, DataMember
    from .routes import main_bp

    app.register_blueprint(main_bp)

    return app
