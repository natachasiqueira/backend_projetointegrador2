from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.usuario import Usuario
from models.psicologo import Psicologo
from models.paciente import Paciente
from extensions import db
from functools import wraps

users_bp = Blueprint('usuarios', __name__)

# Decorador para verificar se o usuário é administrador ou o próprio usuário
def admin_ou_proprio_usuario(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter claims do JWT
        claims = get_jwt()
        usuario_atual_id = get_jwt_identity()
        tipo_usuario = claims.get('tipo_usuario', '')
        
        # Verificar se o ID na URL é o mesmo do usuário atual ou se é admin
        usuario_id = kwargs.get('usuario_id')
        if usuario_id and int(usuario_id) != usuario_atual_id and tipo_usuario != 'admin':
            return jsonify({'mensagem': 'Acesso não autorizado'}), 403
        
        return f(*args, **kwargs)
    return decorated

# Decorador para verificar se o usuário é psicólogo
def somente_psicologo(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter claims do JWT
        claims = get_jwt()
        tipo_usuario = claims.get('tipo_usuario', '')
        
        if tipo_usuario != 'psicologo':
            return jsonify({'mensagem': 'Acesso restrito a psicólogos'}), 403
        
        return f(*args, **kwargs)
    return decorated

@users_bp.route('/usuarios', methods=['GET'])
@jwt_required()
@somente_psicologo
def listar_usuarios():
    # Obter parâmetros de consulta
    tipo = request.args.get('tipo', None)
    
    # Consulta base
    query = Usuario.query
    
    # Filtrar por tipo se especificado
    if tipo:
        query = query.filter_by(tipo_usuario=tipo)
    
    # Executar consulta
    usuarios = query.all()
    
    # Retornar resultados
    return jsonify([usuario.para_dict() for usuario in usuarios]), 200

@users_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@jwt_required()
@admin_ou_proprio_usuario
def obter_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    return jsonify(usuario.para_dict()), 200

@users_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
@admin_ou_proprio_usuario
def atualizar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    dados = request.get_json()
    
    # Atualizar campos permitidos
    if 'nome' in dados:
        usuario.nome = dados['nome']
    if 'email' in dados:
        usuario.email = dados['email']
    if 'telefone' in dados:
        usuario.telefone = dados['telefone']
    if 'senha' in dados and dados['senha']:
        usuario.definir_senha(dados['senha'])
    
    # Se for psicólogo, atualizar informações específicas
    if usuario.tipo_usuario == 'psicologo' and ('registro' in dados or 'especializacao' in dados):
        psicologo = Psicologo.query.filter_by(usuario_id=usuario.id).first()
        
        if psicologo:
            if 'registro' in dados:
                psicologo.registro = dados['registro']
            if 'especializacao' in dados:
                psicologo.especializacao = dados['especializacao']
    
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário atualizado com sucesso'}), 200

@users_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
@admin_ou_proprio_usuario
def excluir_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário excluído com sucesso'}), 200

@users_bp.route('/psicologos', methods=['GET'])
@jwt_required()
def listar_psicologos():
    psicologos = Psicologo.query.all()
    return jsonify([p.para_dict() for p in psicologos]), 200

@users_bp.route('/pacientes', methods=['GET'])
@jwt_required()
@somente_psicologo
def listar_pacientes():
    pacientes = Paciente.query.all()
    return jsonify([p.para_dict() for p in pacientes]), 200