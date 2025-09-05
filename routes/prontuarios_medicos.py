from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.prontuario_medico import ProntuarioMedico
from models.psicologo import Psicologo
from models.paciente import Paciente
from extensions import db
from functools import wraps
from datetime import datetime

medical_records_bp = Blueprint('prontuarios', __name__)

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

# Decorador para verificar se o usuário é o psicólogo ou paciente do prontuário
def psicologo_ou_paciente_do_prontuario(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter ID do usuário atual
        usuario_atual_id = get_jwt_identity()
        claims = get_jwt()
        tipo_usuario = claims.get('tipo_usuario', '')
        
        # Obter ID do prontuário
        prontuario_id = kwargs.get('prontuario_id')
        if not prontuario_id:
            return jsonify({'mensagem': 'ID do prontuário não fornecido'}), 400
        
        # Buscar prontuário
        prontuario = ProntuarioMedico.query.get(prontuario_id)
        if not prontuario:
            return jsonify({'mensagem': 'Prontuário não encontrado'}), 404
        
        # Verificar se o usuário é o psicólogo ou paciente do prontuário
        autorizado = False
        
        if tipo_usuario == 'psicologo':
            psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
            if psicologo and psicologo.id == prontuario.psicologo_id:
                autorizado = True
        elif tipo_usuario == 'paciente':
            paciente = Paciente.query.filter_by(usuario_id=usuario_atual_id).first()
            if paciente and paciente.id == prontuario.paciente_id:
                autorizado = True
        
        if not autorizado:
            return jsonify({'mensagem': 'Acesso não autorizado a este prontuário'}), 403
        
        return f(*args, **kwargs)
    return decorated

@medical_records_bp.route('/prontuarios', methods=['GET'])
@jwt_required()
def listar_prontuarios():
    # Obter ID e tipo do usuário atual
    usuario_atual_id = get_jwt_identity()
    claims = get_jwt()
    tipo_usuario = claims.get('tipo_usuario', '')
    
    # Filtrar prontuários com base no tipo de usuário
    if tipo_usuario == 'psicologo':
        psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
        if not psicologo:
            return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
        
        prontuarios = ProntuarioMedico.query.filter_by(psicologo_id=psicologo.id).all()
    elif tipo_usuario == 'paciente':
        paciente = Paciente.query.filter_by(usuario_id=usuario_atual_id).first()
        if not paciente:
            return jsonify({'mensagem': 'Paciente não encontrado'}), 404
        
        prontuarios = ProntuarioMedico.query.filter_by(paciente_id=paciente.id).all()
    else:
        return jsonify({'mensagem': 'Tipo de usuário não autorizado'}), 403
    
    # Parâmetro de consulta para filtrar por paciente (apenas para psicólogos)
    paciente_id = request.args.get('paciente_id', type=int)
    if tipo_usuario == 'psicologo' and paciente_id:
        prontuarios = [p for p in prontuarios if p.paciente_id == paciente_id]
    
    # Retornar resultados
    return jsonify([prontuario.para_dict(incluir_detalhes=True) for prontuario in prontuarios]), 200

@medical_records_bp.route('/prontuarios/<int:prontuario_id>', methods=['GET'])
@jwt_required()
@psicologo_ou_paciente_do_prontuario
def obter_prontuario(prontuario_id):
    prontuario = ProntuarioMedico.query.get(prontuario_id)
    return jsonify(prontuario.para_dict(incluir_detalhes=True)), 200

@medical_records_bp.route('/prontuarios', methods=['POST'])
@jwt_required()
@somente_psicologo
def criar_prontuario():
    dados = request.get_json()
    
    # Verificar campos obrigatórios
    campos_obrigatorios = ['data', 'conteudo', 'paciente_id']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({'mensagem': f'Campo {campo} é obrigatório'}), 400
    
    # Obter ID do psicólogo atual
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo:
        return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
    
    # Verificar se o paciente existe
    paciente = Paciente.query.get(dados['paciente_id'])
    if not paciente:
        return jsonify({'mensagem': 'Paciente não encontrado'}), 404
    
    # Criar novo prontuário
    novo_prontuario = ProntuarioMedico(
        data=dados['data'],
        conteudo=dados['conteudo'],
        psicologo_id=psicologo.id,
        paciente_id=dados['paciente_id']
    )
    
    db.session.add(novo_prontuario)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Prontuário criado com sucesso',
        'prontuario': novo_prontuario.para_dict()
    }), 201

@medical_records_bp.route('/prontuarios/<int:prontuario_id>', methods=['PUT'])
@jwt_required()
@somente_psicologo
def atualizar_prontuario(prontuario_id):
    prontuario = ProntuarioMedico.query.get(prontuario_id)
    
    if not prontuario:
        return jsonify({'mensagem': 'Prontuário não encontrado'}), 404
    
    # Verificar se o psicólogo atual é o dono do prontuário
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo or psicologo.id != prontuario.psicologo_id:
        return jsonify({'mensagem': 'Acesso não autorizado a este prontuário'}), 403
    
    dados = request.get_json()
    
    # Atualizar campos
    if 'conteudo' in dados:
        prontuario.conteudo = dados['conteudo']
    if 'data' in dados:
        prontuario.data = dados['data']
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Prontuário atualizado com sucesso',
        'prontuario': prontuario.para_dict()
    }), 200

@medical_records_bp.route('/prontuarios/<int:prontuario_id>', methods=['DELETE'])
@jwt_required()
@somente_psicologo
def excluir_prontuario(prontuario_id):
    prontuario = ProntuarioMedico.query.get(prontuario_id)
    
    if not prontuario:
        return jsonify({'mensagem': 'Prontuário não encontrado'}), 404
    
    # Verificar se o psicólogo atual é o dono do prontuário
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo or psicologo.id != prontuario.psicologo_id:
        return jsonify({'mensagem': 'Acesso não autorizado a este prontuário'}), 403
    
    db.session.delete(prontuario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Prontuário excluído com sucesso'}), 200