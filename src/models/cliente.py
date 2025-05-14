from src.models.user import db

class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    endereco = db.Column(db.String(255), nullable=True)
    cpf_cnpj = db.Column(db.String(20), nullable=True, unique=True)
    # Adicionaremos o relacionamento com OrdensDeServico posteriormente
    # ordens_servico = db.relationship('OrdemDeServico', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'cpf_cnpj': self.cpf_cnpj
        }
