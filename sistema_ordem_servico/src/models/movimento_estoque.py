from src.models.user import db
from datetime import datetime

class MovimentoEstoque(db.Model):
    __tablename__ = "movimentos_estoque"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # "entrada", "saida", "ajuste_entrada", "ajuste_saida"
    quantidade = db.Column(db.Integer, nullable=False)
    data_movimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    observacao = db.Column(db.String(255), nullable=True)
    # Opcional: relacionar com OS ou Compra
    # ordem_servico_id = db.Column(db.Integer, db.ForeignKey("ordens_de_servico.id"), nullable=True)
    # compra_id = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=True) # Se houver módulo de compras

    produto = db.relationship("Produto", backref=db.backref("movimentacoes_estoque", lazy="dynamic"))

    def __repr__(self):
        return f"<MovimentoEstoque {self.id} - Produto {self.produto_id} - {self.tipo} - {self.quantidade}>"

    def to_dict(self):
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "data_movimento": self.data_movimento.isoformat(),
            "observacao": self.observacao,
            # "ordem_servico_id": self.ordem_servico_id,
            "produto_descricao": self.produto.descricao if self.produto else None
        }
