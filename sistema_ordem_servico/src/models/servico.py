from src.models.user import db

class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    tempo_estimado_horas = db.Column(db.Float, nullable=True) # Em horas

    def __repr__(self):
        return f'<Servico {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'tempo_estimado_horas': self.tempo_estimado_horas
        }
