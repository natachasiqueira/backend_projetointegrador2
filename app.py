from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from extensions import db, migrate
from routes.autenticacao import auth_bp
from routes.usuarios import users_bp
from routes.agendamentos import appointments_bp
from routes.prontuarios_medicos import medical_records_bp
from routes.analises import analytics_bp
from swagger import configure_swagger

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    
    # Configurar Swagger
    if config_name != 'testing':
        swagger = configure_swagger(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(medical_records_bp, url_prefix='/api/medical-records')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Rota de teste
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok", "message": "API da Clínica Mentalize está funcionando!"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)