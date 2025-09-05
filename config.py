import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-para-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-chave-secreta-padrao'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False
    # Em produção, certifique-se de definir variáveis de ambiente adequadas

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}