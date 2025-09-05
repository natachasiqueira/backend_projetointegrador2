from extensions import db
from datetime import datetime
from passlib.hash import pbkdf2_sha256

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(64), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    tipo_usuario = db.Column(db.String(20), nullable=False)  # 'paciente' ou 'psicologo'
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    psicologo = db.relationship('Psicologo', backref='usuario', uselist=False, cascade='all, delete-orphan')
    paciente = db.relationship('Paciente', backref='usuario', uselist=False, cascade='all, delete-orphan')
    
    def definir_senha(self, senha):
        self.senha_hash = pbkdf2_sha256.hash(senha)
    
    def verificar_senha(self, senha):
        return pbkdf2_sha256.verify(senha, self.senha_hash)
    
    def __repr__(self):
        return f'<Usuario {self.nome_usuario}>'
    
    def para_dict(self):
        return {
            'id': self.id,
            'nome_usuario': self.nome_usuario,
            'email': self.email,
            'nome': self.nome,
            'telefone': self.telefone,
            'tipo_usuario': self.tipo_usuario,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }