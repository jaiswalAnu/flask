from flask import Flask
from app.config import Config
from app.extensions import db, ma, migrate
from app.routes import note_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(note_bp, url_prefix='/api')
    return app