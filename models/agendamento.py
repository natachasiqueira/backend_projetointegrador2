from extensions import db
from datetime import datetime

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False)  # Formato: YYYY-MM-DD
    hora = db.Column(db.String(5), nullable=False)   # Formato: HH:MM
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, confirmado, cancelado, concluído
    observacoes = db.Column(db.Text, nullable=True)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Agendamento {self.id}> Data: {self.data}, Hora: {self.hora}'
    
    def para_dict(self, incluir_detalhes=False):
        resultado = {
            'id': self.id,
            'data': self.data,
            'hora': self.hora,
            'status': self.status,
            'observacoes': self.observacoes,
            'psicologo_id': self.psicologo_id,
            'paciente_id': self.paciente_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
        
        if incluir_detalhes:
            resultado['psicologo'] = self.psicologo.para_dict() if self.psicologo else None
            resultado['paciente'] = self.paciente.para_dict() if self.paciente else None
        
        return resultado