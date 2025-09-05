import pytest
from app import create_app
from extensions import db
from models.usuario import Usuario
from models.psicologo import Psicologo
from models.paciente import Paciente
from models.agendamento import Agendamento
import json
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Criar usuário de teste (psicólogo)
        usuario_psicologo = Usuario(
            nome_usuario='psicologo_teste',
            email='psicologo@teste.com',
            nome='Psicólogo Teste',
            telefone='11999999999',
            tipo_usuario='psicologo'
        )
        usuario_psicologo.definir_senha('senha123')
        db.session.add(usuario_psicologo)
        db.session.commit()
        
        # Criar registro de psicólogo
        psicologo = Psicologo(
            usuario_id=usuario_psicologo.id,
            registro='CRP 12345',
            especializacao='Terapia Cognitivo-Comportamental'
        )
        db.session.add(psicologo)
        db.session.commit()
        
        # Criar usuário de teste (paciente)
        usuario_paciente = Usuario(
            nome_usuario='paciente_teste',
            email='paciente@teste.com',
            nome='Paciente Teste',
            telefone='11988888888',
            tipo_usuario='paciente'
        )
        usuario_paciente.definir_senha('senha123')
        db.session.add(usuario_paciente)
        db.session.commit()
        
        # Criar registro de paciente
        paciente = Paciente(
            usuario_id=usuario_paciente.id
        )
        db.session.add(paciente)
        db.session.commit()
        
        # Criar agendamento de teste
        data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        agendamento = Agendamento(
            data=data_amanha,
            hora='14:00',
            status='pendente',
            observacoes='Consulta inicial',
            psicologo_id=psicologo.id,
            paciente_id=paciente.id
        )
        db.session.add(agendamento)
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token_psicologo(client):
    # Obter token JWT para o psicólogo
    resposta = client.post('/login', json={
        'nome_usuario': 'psicologo_teste',
        'senha': 'senha123'
    })
    
    dados = json.loads(resposta.data)
    return dados['token']

@pytest.fixture
def token_paciente(client):
    # Obter token JWT para o paciente
    resposta = client.post('/login', json={
        'nome_usuario': 'paciente_teste',
        'senha': 'senha123'
    })
    
    dados = json.loads(resposta.data)
    return dados['token']

def test_listar_agendamentos_psicologo(client, token_psicologo):
    # Teste de listagem de agendamentos para psicólogo
    resposta = client.get('/agendamentos', headers={
        'Authorization': f'Bearer {token_psicologo}'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 200
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert 'data' in dados[0]
    assert 'hora' in dados[0]
    assert 'status' in dados[0]

def test_listar_agendamentos_paciente(client, token_paciente):
    # Teste de listagem de agendamentos para paciente
    resposta = client.get('/agendamentos', headers={
        'Authorization': f'Bearer {token_paciente}'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 200
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert 'data' in dados[0]
    assert 'hora' in dados[0]
    assert 'status' in dados[0]

def test_criar_agendamento(client, token_psicologo, app):
    # Teste de criação de agendamento
    with app.app_context():
        paciente = Paciente.query.first()
        
        data_futura = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        resposta = client.post('/agendamentos', 
            headers={'Authorization': f'Bearer {token_psicologo}'},
            json={
                'data': data_futura,
                'hora': '15:30',
                'paciente_id': paciente.id,
                'observacoes': 'Sessão de acompanhamento'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 201
        assert 'mensagem' in dados
        assert 'Agendamento criado com sucesso' in dados['mensagem']
        assert 'agendamento' in dados
        assert dados['agendamento']['data'] == data_futura
        assert dados['agendamento']['hora'] == '15:30'

def test_atualizar_agendamento_psicologo(client, token_psicologo, app):
    # Teste de atualização de agendamento por psicólogo
    with app.app_context():
        agendamento = Agendamento.query.first()
        
        resposta = client.put(f'/agendamentos/{agendamento.id}', 
            headers={'Authorization': f'Bearer {token_psicologo}'},
            json={
                'status': 'confirmado',
                'observacoes': 'Confirmado por telefone'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 200
        assert 'mensagem' in dados
        assert 'Agendamento atualizado com sucesso' in dados['mensagem']
        assert 'agendamento' in dados
        assert dados['agendamento']['status'] == 'confirmado'
        assert dados['agendamento']['observacoes'] == 'Confirmado por telefone'

def test_cancelar_agendamento_paciente(client, token_paciente, app):
    # Teste de cancelamento de agendamento por paciente
    with app.app_context():
        agendamento = Agendamento.query.first()
        
        resposta = client.put(f'/agendamentos/{agendamento.id}', 
            headers={'Authorization': f'Bearer {token_paciente}'},
            json={
                'status': 'cancelado'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 200
        assert 'mensagem' in dados
        assert 'Agendamento atualizado com sucesso' in dados['mensagem']
        assert 'agendamento' in dados
        assert dados['agendamento']['status'] == 'cancelado'

def test_paciente_nao_pode_alterar_outros_campos(client, token_paciente, app):
    # Teste que paciente não pode alterar outros campos além do status
    with app.app_context():
        agendamento = Agendamento.query.first()
        
        resposta = client.put(f'/agendamentos/{agendamento.id}', 
            headers={'Authorization': f'Bearer {token_paciente}'},
            json={
                'observacoes': 'Tentando alterar observações'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 403
        assert 'mensagem' in dados
        assert 'Pacientes só podem cancelar agendamentos' in dados['mensagem']