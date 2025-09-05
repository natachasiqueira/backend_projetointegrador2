from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.agendamento import Agendamento
from models.prontuario_medico import ProntuarioMedico
from models.psicologo import Psicologo
from models.paciente import Paciente
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analises', __name__)

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

@analytics_bp.route('/analises/agendamentos', methods=['GET'])
@jwt_required()
@somente_psicologo
def analise_agendamentos():
    # Obter ID do psicólogo atual
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo:
        return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
    
    # Obter todos os agendamentos do psicólogo
    agendamentos = Agendamento.query.filter_by(psicologo_id=psicologo.id).all()
    
    # Calcular estatísticas
    total_agendamentos = len(agendamentos)
    
    # Contagem por status
    status_counts = {}
    for agendamento in agendamentos:
        status = agendamento.status
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    # Agendamentos por dia da semana
    dias_semana = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    agendamentos_por_dia = {dia: 0 for dia in dias_semana.values()}
    
    for agendamento in agendamentos:
        try:
            data = datetime.strptime(agendamento.data, '%Y-%m-%d')
            dia_semana = dias_semana[data.weekday()]
            agendamentos_por_dia[dia_semana] += 1
        except ValueError:
            # Ignorar datas em formato inválido
            pass
    
    # Calcular taxa de comparecimento (agendamentos concluídos / total de agendamentos passados)
    agendamentos_passados = [a for a in agendamentos if a.status in ['concluído', 'cancelado']]
    total_passados = len(agendamentos_passados)
    concluidos = len([a for a in agendamentos_passados if a.status == 'concluído'])
    
    taxa_comparecimento = (concluidos / total_passados) * 100 if total_passados > 0 else 0
    
    return jsonify({
        'total_agendamentos': total_agendamentos,
        'por_status': status_counts,
        'por_dia_semana': agendamentos_por_dia,
        'taxa_comparecimento': round(taxa_comparecimento, 2)
    }), 200

@analytics_bp.route('/analises/prontuarios', methods=['GET'])
@jwt_required()
@somente_psicologo
def analise_prontuarios():
    # Obter ID do psicólogo atual
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo:
        return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
    
    # Obter todos os prontuários do psicólogo
    prontuarios = ProntuarioMedico.query.filter_by(psicologo_id=psicologo.id).all()
    
    # Calcular estatísticas
    total_prontuarios = len(prontuarios)
    
    # Prontuários por paciente
    prontuarios_por_paciente = {}
    for prontuario in prontuarios:
        paciente_id = prontuario.paciente_id
        if paciente_id in prontuarios_por_paciente:
            prontuarios_por_paciente[paciente_id] += 1
        else:
            prontuarios_por_paciente[paciente_id] = 1
    
    # Converter IDs de pacientes para nomes
    prontuarios_por_paciente_nome = {}
    for paciente_id, count in prontuarios_por_paciente.items():
        paciente = Paciente.query.get(paciente_id)
        if paciente and paciente.usuario:
            nome_paciente = paciente.usuario.nome
            prontuarios_por_paciente_nome[nome_paciente] = count
    
    # Prontuários por mês
    prontuarios_por_mes = {}
    for prontuario in prontuarios:
        try:
            data = datetime.strptime(prontuario.data, '%Y-%m-%d')
            mes_ano = data.strftime('%Y-%m')
            if mes_ano in prontuarios_por_mes:
                prontuarios_por_mes[mes_ano] += 1
            else:
                prontuarios_por_mes[mes_ano] = 1
        except ValueError:
            # Ignorar datas em formato inválido
            pass
    
    # Ordenar por mês
    prontuarios_por_mes = dict(sorted(prontuarios_por_mes.items()))
    
    return jsonify({
        'total_prontuarios': total_prontuarios,
        'por_paciente': prontuarios_por_paciente_nome,
        'por_mes': prontuarios_por_mes
    }), 200

@analytics_bp.route('/analises/pacientes', methods=['GET'])
@jwt_required()
@somente_psicologo
def analise_pacientes():
    # Obter ID do psicólogo atual
    usuario_atual_id = get_jwt_identity()
    psicologo = Psicologo.query.filter_by(usuario_id=usuario_atual_id).first()
    
    if not psicologo:
        return jsonify({'mensagem': 'Psicólogo não encontrado'}), 404
    
    # Obter todos os agendamentos do psicólogo
    agendamentos = Agendamento.query.filter_by(psicologo_id=psicologo.id).all()
    
    # Agrupar agendamentos por paciente
    agendamentos_por_paciente = {}
    for agendamento in agendamentos:
        paciente_id = agendamento.paciente_id
        if paciente_id not in agendamentos_por_paciente:
            agendamentos_por_paciente[paciente_id] = []
        agendamentos_por_paciente[paciente_id].append(agendamento)
    
    # Calcular estatísticas por paciente
    estatisticas_pacientes = []
    
    for paciente_id, agendamentos_paciente in agendamentos_por_paciente.items():
        paciente = Paciente.query.get(paciente_id)
        if not paciente or not paciente.usuario:
            continue
        
        # Contar agendamentos por status
        status_counts = {}
        for agendamento in agendamentos_paciente:
            status = agendamento.status
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1
        
        # Calcular taxa de comparecimento
        agendamentos_passados = [a for a in agendamentos_paciente if a.status in ['concluído', 'cancelado']]
        total_passados = len(agendamentos_passados)
        concluidos = len([a for a in agendamentos_passados if a.status == 'concluído'])
        
        taxa_comparecimento = (concluidos / total_passados) * 100 if total_passados > 0 else 0
        
        # Contar prontuários
        prontuarios = ProntuarioMedico.query.filter_by(
            psicologo_id=psicologo.id,
            paciente_id=paciente_id
        ).all()
        
        estatisticas_pacientes.append({
            'paciente_id': paciente_id,
            'nome': paciente.usuario.nome,
            'total_agendamentos': len(agendamentos_paciente),
            'agendamentos_por_status': status_counts,
            'taxa_comparecimento': round(taxa_comparecimento, 2),
            'total_prontuarios': len(prontuarios)
        })
    
    return jsonify(estatisticas_pacientes), 200