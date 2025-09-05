import pytest
from app import create_app
from extensions import db
from models.usuario import Usuario
from models.psicologo import Psicologo
from models.paciente import Paciente
import json

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
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_sucesso(client):
    # Teste de login com credenciais válidas
    resposta = client.post('/login', json={
        'nome_usuario': 'psicologo_teste',
        'senha': 'senha123'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 200
    assert 'token' in dados
    assert dados['tipo_usuario'] == 'psicologo'

def test_login_falha(client):
    # Teste de login com credenciais inválidas
    resposta = client.post('/login', json={
        'nome_usuario': 'psicologo_teste',
        'senha': 'senha_errada'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 401
    assert 'mensagem' in dados
    assert 'Credenciais inválidas' in dados['mensagem']

def test_registro_sucesso(client):
    # Teste de registro de novo usuário
    resposta = client.post('/registro', json={
        'nome_usuario': 'novo_usuario',
        'senha': 'senha123',
        'email': 'novo@teste.com',
        'nome': 'Novo Usuário',
        'telefone': '11977777777',
        'tipo_usuario': 'paciente'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 201
    assert 'mensagem' in dados
    assert 'Usuário registrado com sucesso' in dados['mensagem']
    assert 'id' in dados

def test_registro_psicologo_sucesso(client):
    # Teste de registro de novo psicólogo
    resposta = client.post('/registro', json={
        'nome_usuario': 'novo_psicologo',
        'senha': 'senha123',
        'email': 'novo_psicologo@teste.com',
        'nome': 'Novo Psicólogo',
        'telefone': '11966666666',
        'tipo_usuario': 'psicologo',
        'registro': 'CRP 54321',
        'especializacao': 'Psicanálise'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 201
    assert 'mensagem' in dados
    assert 'Usuário registrado com sucesso' in dados['mensagem']
    assert 'id' in dados

def test_registro_falha_usuario_existente(client):
    # Teste de registro com nome de usuário já existente
    resposta = client.post('/registro', json={
        'nome_usuario': 'psicologo_teste',  # Nome de usuário já existente
        'senha': 'senha123',
        'email': 'outro@teste.com',
        'nome': 'Outro Usuário',
        'telefone': '11955555555',
        'tipo_usuario': 'paciente'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 400
    assert 'mensagem' in dados
    assert 'Nome de usuário já existe' in dados['mensagem']

def test_registro_falha_email_existente(client):
    # Teste de registro com email já existente
    resposta = client.post('/registro', json={
        'nome_usuario': 'outro_usuario',
        'senha': 'senha123',
        'email': 'psicologo@teste.com',  # Email já existente
        'nome': 'Outro Usuário',
        'telefone': '11944444444',
        'tipo_usuario': 'paciente'
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 400
    assert 'mensagem' in dados
    assert 'Email já está em uso' in dados['mensagem']

def test_registro_falha_tipo_usuario_invalido(client):
    # Teste de registro com tipo de usuário inválido
    resposta = client.post('/registro', json={
        'nome_usuario': 'outro_usuario',
        'senha': 'senha123',
        'email': 'outro@teste.com',
        'nome': 'Outro Usuário',
        'telefone': '11933333333',
        'tipo_usuario': 'admin'  # Tipo inválido
    })
    
    dados = json.loads(resposta.data)
    
    assert resposta.status_code == 400
    assert 'mensagem' in dados
    assert 'Tipo de usuário inválido' in dados['mensagem']