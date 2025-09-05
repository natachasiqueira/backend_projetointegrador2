from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.usuario import Usuario
from extensions import db
import datetime

auth_bp = Blueprint('autenticacao', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    
    if not dados or not dados.get('nome_usuario') or not dados.get('senha'):
        return jsonify({'mensagem': 'Nome de usuário e senha são obrigatórios'}), 400
    
    usuario = Usuario.query.filter_by(nome_usuario=dados.get('nome_usuario')).first()
    
    if not usuario or not usuario.verificar_senha(dados.get('senha')):
        return jsonify({'mensagem': 'Credenciais inválidas'}), 401
    
    # Criar token JWT com expiração de 1 dia
    expira = datetime.timedelta(days=1)
    token_acesso = create_access_token(
        identity=usuario.id,
        additional_claims={'tipo_usuario': usuario.tipo_usuario},
        expires_delta=expira
    )
    
    return jsonify({
        'token': token_acesso,
        'tipo_usuario': usuario.tipo_usuario,
        'id': usuario.id,
        'nome': usuario.nome
    }), 200

@auth_bp.route('/registro', methods=['POST'])
def registro():
    dados = request.get_json()
    
    # Verificar se todos os campos obrigatórios estão presentes
    campos_obrigatorios = ['nome_usuario', 'senha', 'email', 'nome', 'telefone', 'tipo_usuario']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({'mensagem': f'Campo {campo} é obrigatório'}), 400
    
    # Verificar se o tipo de usuário é válido
    if dados['tipo_usuario'] not in ['paciente', 'psicologo']:
        return jsonify({'mensagem': 'Tipo de usuário inválido. Deve ser "paciente" ou "psicologo"'}), 400
    
    # Verificar se o nome de usuário já existe
    if Usuario.query.filter_by(nome_usuario=dados['nome_usuario']).first():
        return jsonify({'mensagem': 'Nome de usuário já existe'}), 400
    
    # Verificar se o email já existe
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'mensagem': 'Email já está em uso'}), 400
    
    # Criar novo usuário
    novo_usuario = Usuario(
        nome_usuario=dados['nome_usuario'],
        email=dados['email'],
        nome=dados['nome'],
        telefone=dados['telefone'],
        tipo_usuario=dados['tipo_usuario']
    )
    novo_usuario.definir_senha(dados['senha'])
    
    # Adicionar ao banco de dados
    db.session.add(novo_usuario)
    db.session.commit()
    
    # Se for psicólogo, criar registro de psicólogo
    if dados['tipo_usuario'] == 'psicologo':
        from models.psicologo import Psicologo
        
        if 'registro' not in dados or 'especializacao' not in dados:
            return jsonify({'mensagem': 'Registro (CRP) e especialização são obrigatórios para psicólogos'}), 400
        
        novo_psicologo = Psicologo(
            usuario_id=novo_usuario.id,
            registro=dados['registro'],
            especializacao=dados['especializacao']
        )
        
        db.session.add(novo_psicologo)
        db.session.commit()
    
    # Se for paciente, criar registro de paciente
    if dados['tipo_usuario'] == 'paciente':
        from models.paciente import Paciente
        
        novo_paciente = Paciente(
            usuario_id=novo_usuario.id
        )
        
        db.session.add(novo_paciente)
        db.session.commit()
    
    return jsonify({'mensagem': 'Usuário registrado com sucesso', 'id': novo_usuario.id}), 201

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado'}), 404
    
    return jsonify(usuario.para_dict()), 200