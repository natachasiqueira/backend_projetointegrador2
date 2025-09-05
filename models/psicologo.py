from extensions import db
from datetime import datetime

class Psicologo(db.Model):
    __tablename__ = 'psicologos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    registro = db.Column(db.String(20), nullable=False)  # Número de registro no CRP
    especializacao = db.Column(db.String(100), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='psicologo', lazy='dynamic', cascade='all, delete-orphan')
    prontuarios = db.relationship('ProntuarioMedico', backref='psicologo', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Psicologo {self.id}> Registro: {self.registro}'
    
    def para_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'registro': self.registro,
            'especializacao': self.especializacao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'usuario': self.usuario.para_dict() if self.usuario else None
        }