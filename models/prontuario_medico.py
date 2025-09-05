from extensions import db
from datetime import datetime

class ProntuarioMedico(db.Model):
    __tablename__ = 'prontuarios_medicos'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False)  # Formato: YYYY-MM-DD
    conteudo = db.Column(db.Text, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProntuarioMedico {self.id}> Data: {self.data}'
    
    def para_dict(self, incluir_detalhes=False):
        resultado = {
            'id': self.id,
            'data': self.data,
            'conteudo': self.conteudo,
            'paciente_id': self.paciente_id,
            'psicologo_id': self.psicologo_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
        
        if incluir_detalhes:
            resultado['paciente'] = self.paciente.para_dict() if self.paciente else None
            resultado['psicologo'] = self.psicologo.para_dict() if self.psicologo else None
        
        return resultado