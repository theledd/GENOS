from src.models.user import db

class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_barra = db.Column(db.String(100), nullable=True, unique=True)
    descricao = db.Column(db.String(255), nullable=False)
    tipo_movimento = db.Column(db.String(50), nullable=True) # Entrada, Saída
    preco_compra = db.Column(db.Float, nullable=True)
    preco_venda = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(50), nullable=True)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    # Adicionaremos relacionamentos se necessário, por exemplo, com OrdensDeServicoProduto

    def __repr__(self):
        return f'<Produto {self.descricao}>'

    def to_dict(self):
        return {
            'id': self.id,
            'codigo_barra': self.codigo_barra,
            'descricao': self.descricao,
            'tipo_movimento': self.tipo_movimento,
            'preco_compra': self.preco_compra,
            'preco_venda': self.preco_venda,
            'unidade': self.unidade,
            'estoque': self.estoque
        }
