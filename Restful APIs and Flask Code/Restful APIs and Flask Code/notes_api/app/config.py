import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///notes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_DOC_EXTENSION = 'list'
    RESTX_MASK_SWAGGER = False
    SECRET_KEY = os.getenv('SECRET_KEY','default_secret_key')
    RESTX_SWAGGER_UI = True