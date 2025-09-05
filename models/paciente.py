from extensions import db
from datetime import datetime

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    prontuarios = db.relationship('ProntuarioMedico', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Paciente {self.id}>'
    
    def para_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'usuario': self.usuario.para_dict() if self.usuario else None
        }