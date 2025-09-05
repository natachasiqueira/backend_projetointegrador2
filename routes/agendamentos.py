from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.agendamento import Agendamento
from models.psicologo import Psicologo
from models.paciente import Paciente
from extensions import db
from functools import wraps
from datetime import datetime

appointments_bp = Blueprint('agendamentos', __name__)

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

# Decorador para verificar se o usuário é o psicólogo ou paciente do agendamento
def psicologo_ou_paciente_do_agendamento(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter ID do usuário atual
        usuario_atual_id = get_jwt_identity()
        claims = get_jwt()
        tipo_usuario = claims.get('tipo_usuario', '')
        
        # Obter ID do agendamento
        agendamento_id = kwargs.get('agendamento_id')
        if not agendamento_id:
            return jsonify({'mensagem': 'ID do agendamento não fornecido'}), 400
        
        # Buscar agendamento
        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            return jsonify({'mensagem': 'Agendamento não encontrado'}), 404
        
        # Verificar se o usuário é o psicólogo ou paciente do agendamento
        autorizado = False
        
        if tipo_usuario == 'psicologo':
            psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
            if psicologo and psicologo.id == agendamento.psicologo_id:
                autorizado = True
        elif tipo_usuario == 'paciente':
            paciente = Paciente.query.filter_by(usuario_id=usuario_atual_id).first()
            if paciente and paciente.id == agendamento.paciente_id:
                autorizado = True
        
        if not autorizado:
            return jsonify({'mensagem': 'Acesso não autorizado a este agendamento'}), 403
        
        return f(*args, **kwargs)
    return decorated

@appointments_bp.route('/agendamentos', methods=['GET'])
@jwt_required()
def listar_agendamentos():
    # Obter ID e tipo do usuário atual
    usuario_atual_id = get_jwt_identity()
    claims = get_jwt()
    tipo_usuario = claims.get('tipo_usuario', '')
    
    # Filtrar agendamentos com base no tipo de usuário
    if tipo_usuario == 'psicologo':
        psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
        if not psicologo:
            return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
        
        agendamentos = Agendamento.query.filter_by(psicologo_id=psicologo.id).all()
    elif tipo_usuario == 'paciente':
        paciente = Paciente.query.filter_by(usuario_id=usuario_atual_id).first()
        if not paciente:
            return jsonify({'mensagem': 'Paciente não encontrado'}), 404
        
        agendamentos = Agendamento.query.filter_by(paciente_id=paciente.id).all()
    else:
        return jsonify({'mensagem': 'Tipo de usuário não autorizado'}), 403
    
    # Retornar resultados
    return jsonify([agendamento.para_dict(incluir_detalhes=True) for agendamento in agendamentos]), 200

@appointments_bp.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
@jwt_required()
@psicologo_ou_paciente_do_agendamento
def obter_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    return jsonify(agendamento.para_dict(incluir_detalhes=True)), 200

@appointments_bp.route('/agendamentos', methods=['POST'])
@jwt_required()
@somente_psicologo
def criar_agendamento():
    dados = request.get_json()
    
    # Verificar campos obrigatórios
    campos_obrigatorios = ['data', 'hora', 'paciente_id']
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
    
    # Verificar se já existe um agendamento para o mesmo psicólogo, data e hora
    agendamento_existente = Agendamento.query.filter_by(
        psicologo_id=psicologo.id,
        data=dados['data'],
        hora=dados['hora']
    ).first()
    
    if agendamento_existente:
        return jsonify({'mensagem': 'Já existe um agendamento para esta data e hora'}), 400
    
    # Criar novo agendamento
    novo_agendamento = Agendamento(
        data=dados['data'],
        hora=dados['hora'],
        status='pendente',
        observacoes=dados.get('observacoes', ''),
        psicologo_id=psicologo.id,
        paciente_id=dados['paciente_id']
    )
    
    db.session.add(novo_agendamento)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Agendamento criado com sucesso',
        'agendamento': novo_agendamento.para_dict()
    }), 201

@appointments_bp.route('/agendamentos/<int:agendamento_id>', methods=['PUT'])
@jwt_required()
@psicologo_ou_paciente_do_agendamento
def atualizar_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    dados = request.get_json()
    
    # Obter tipo do usuário atual
    claims = get_jwt()
    tipo_usuario = claims.get('tipo_usuario', '')
    
    # Verificar quais campos podem ser atualizados com base no tipo de usuário
    if tipo_usuario == 'psicologo':
        # Psicólogos podem atualizar todos os campos
        if 'data' in dados:
            agendamento.data = dados['data']
        if 'hora' in dados:
            agendamento.hora = dados['hora']
        if 'status' in dados:
            agendamento.status = dados['status']
        if 'observacoes' in dados:
            agendamento.observacoes = dados['observacoes']
    elif tipo_usuario == 'paciente':
        # Pacientes só podem atualizar o status (para cancelar)
        if 'status' in dados and dados['status'] == 'cancelado':
            agendamento.status = 'cancelado'
        else:
            return jsonify({'mensagem': 'Pacientes só podem cancelar agendamentos'}), 403
    
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Agendamento atualizado com sucesso',
        'agendamento': agendamento.para_dict()
    }), 200

@appointments_bp.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
@jwt_required()
@somente_psicologo
def excluir_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)
    
    if not agendamento:
        return jsonify({'mensagem': 'Agendamento não encontrado'}), 404
    
    # Verificar se o psicólogo atual é o dono do agendamento
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo or psicologo.id != agendamento.psicologo_id:
        return jsonify({'mensagem': 'Acesso não autorizado a este agendamento'}), 403
    
    db.session.delete(agendamento)
    db.session.commit()
    
    return jsonify({'mensagem': 'Agendamento excluído com sucesso'}), 200