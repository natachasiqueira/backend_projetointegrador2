from flask import Blueprint, jsonify
from flasgger import Swagger

def configure_swagger(app):
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    template = {
        "swagger": "2.0",
        "info": {
            "title": "API da Clínica Mentalize",
            "description": "API para gerenciamento de pacientes, psicólogos, agendamentos e prontuários médicos",
            "version": "1.0.0",
            "contact": {
                "email": "contato@clinicamentalize.com"
            }
        },
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header usando o esquema Bearer. Exemplo: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }
    
    swagger = Swagger(app, config=swagger_config, template=template)
    return swagger