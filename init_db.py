from app import create_app
from extensions import db
from models import Usuario, Psicologo, Paciente
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        # Verificar se já existem dados
        if Usuario.query.count() > 0:
            print('Banco de dados já inicializado!')
            return
        
        # Criar usuário psicólogo
        psychologist_user = Usuario(
            nome_usuario='cicera.santana',
            email='cicera.santana@clinicamentalize.com',
            nome='Cícera Santana',
            telefone='(11) 98765-4321',
            tipo_usuario='psicologo'
        )
        psychologist_user.definir_senha('senha123')
        db.session.add(psychologist_user)
        db.session.commit()
        
        # Criar psicólogo
        psychologist = Psicologo(
            usuario_id=psychologist_user.id,
            registro='CRP 12345',
            especializacao='Psicologia Clínica'
        )
        db.session.add(psychologist)
        
        # Criar usuários pacientes
        patient1_user = Usuario(
            nome_usuario='maria.oliveira',
            email='maria@example.com',
            nome='Maria Oliveira',
            telefone='(11) 91234-5678',
            tipo_usuario='paciente'
        )
        patient1_user.definir_senha('senha456')
        db.session.add(patient1_user)
        
        patient2_user = Usuario(
            nome_usuario='joao.santos',
            email='joao@example.com',
            nome='João Santos',
            telefone='(11) 98765-1234',
            tipo_usuario='paciente'
        )
        patient2_user.definir_senha('senha789')
        db.session.add(patient2_user)
        db.session.commit()
        
        # Criar pacientes
        patient1 = Paciente(usuario_id=patient1_user.id)
        patient2 = Paciente(usuario_id=patient2_user.id)
        db.session.add(patient1)
        db.session.add(patient2)
        db.session.commit()
        
        print('Banco de dados inicializado com sucesso!')

if __name__ == '__main__':
    init_db()