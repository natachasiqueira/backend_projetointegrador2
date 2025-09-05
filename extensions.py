from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()