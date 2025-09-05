import pytest
from app import create_app
from extensions import db
from models.usuario import Usuario
from models.psicologo import Psicologo
from models.paciente import Paciente
from models.prontuario_medico import ProntuarioMedico
import json
from datetime import datetime

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
        
        # Criar prontuário de teste
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        prontuario = ProntuarioMedico(
            data=data_hoje,
            conteudo='Primeira consulta. Paciente relata ansiedade e dificuldade para dormir.',
            psicologo_id=psicologo.id,
            paciente_id=paciente.id
        )
        db.session.add(prontuario)
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

def test_listar_prontuarios_psicologo(client, token_psicologo):
    # Teste de listagem de prontuários para psicólogo
    resposta = client.get('/prontuarios', headers={
        'Authorization': f'Bearer {token_psicologo}'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 200
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert 'data' in dados[0]
    assert 'conteudo' in dados[0]
    assert 'paciente_id' in dados[0]

def test_listar_prontuarios_paciente(client, token_paciente):
    # Teste de listagem de prontuários para paciente
    resposta = client.get('/prontuarios', headers={
        'Authorization': f'Bearer {token_paciente}'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 200
    assert isinstance(dados, list)
    assert len(dados) > 0
    assert 'data' in dados[0]
    assert 'conteudo' in dados[0]
    assert 'psicologo_id' in dados[0]

def test_criar_prontuario(client, token_psicologo, app):
    # Teste de criação de prontuário
    with app.app_context():
        paciente = Paciente.query.first()
        
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        resposta = client.post('/prontuarios', 
            headers={'Authorization': f'Bearer {token_psicologo}'},
            json={
                'data': data_hoje,
                'conteudo': 'Paciente apresenta melhora nos sintomas de ansiedade após início do tratamento.',
                'paciente_id': paciente.id
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 201
        assert 'mensagem' in dados
        assert 'Prontuário criado com sucesso' in dados['mensagem']
        assert 'prontuario' in dados
        assert dados['prontuario']['data'] == data_hoje

def test_paciente_nao_pode_criar_prontuario(client, token_paciente, app):
    # Teste que paciente não pode criar prontuário
    with app.app_context():
        paciente = Paciente.query.first()
        psicologo = Psicologo.query.first()
        
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        resposta = client.post('/prontuarios', 
            headers={'Authorization': f'Bearer {token_paciente}'},
            json={
                'data': data_hoje,
                'conteudo': 'Tentando criar um prontuário como paciente.',
                'paciente_id': paciente.id,
                'psicologo_id': psicologo.id
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 403
        assert 'mensagem' in dados
        assert 'Acesso restrito a psicólogos' in dados['mensagem']

def test_atualizar_prontuario(client, token_psicologo, app):
    # Teste de atualização de prontuário
    with app.app_context():
        prontuario = ProntuarioMedico.query.first()
        
        resposta = client.put(f'/prontuarios/{prontuario.id}', 
            headers={'Authorization': f'Bearer {token_psicologo}'},
            json={
                'conteudo': 'Conteúdo atualizado do prontuário.'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 200
        assert 'mensagem' in dados
        assert 'Prontuário atualizado com sucesso' in dados['mensagem']
        assert 'prontuario' in dados
        assert dados['prontuario']['conteudo'] == 'Conteúdo atualizado do prontuário.'

def test_paciente_nao_pode_atualizar_prontuario(client, token_paciente, app):
    # Teste que paciente não pode atualizar prontuário
    with app.app_context():
        prontuario = ProntuarioMedico.query.first()
        
        resposta = client.put(f'/prontuarios/{prontuario.id}', 
            headers={'Authorization': f'Bearer {token_paciente}'},
            json={
                'conteudo': 'Tentando atualizar como paciente.'
            }
        )
        
        dados = json.loads(resposta.data)
        
        assert resposta.status_code == 403
        assert 'mensagem' in dados
        assert 'Acesso restrito a psicólogos' in dados['mensagem']