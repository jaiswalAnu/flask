from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
db = SQLAlchemy()
cache = Cache()
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app)
    # SQLAlchemy Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Caching Configuration
    app.config['CACHE_TYPE'] = os.getenv('CACHE_TYPE')
    app.config['CACHE_REDIS_URL'] = os.getenv('CACHE_REDIS_URL')
    app.config['CACHE_REDIS_PORT'] = os.getenv('CACHE_REDIS_PORT')
    app.config['CACHE_DEFAULT_TIMEOUT'] = os.getenv('CACHE_DEFAULT_TIMEOUT')  # Cache timeout in seconds
    db.init_app(app)
    cache.init_app(app)

     # Ensure tables are created when the app starts
    
    from app.routes import sentiment_bp
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')

    return app