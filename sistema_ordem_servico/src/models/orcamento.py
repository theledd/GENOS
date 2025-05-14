from src.models.user import db
from datetime import datetime, timedelta

# Tabela de associação para itens do orçamento (similar à OS)
orcamento_produto = db.Table("orcamento_produto",
    db.Column("orcamento_id", db.Integer, db.ForeignKey("orcamentos.id"), primary_key=True),
    db.Column("produto_id", db.Integer, db.ForeignKey("produtos.id"), primary_key=True),
    db.Column("quantidade", db.Integer, nullable=False, default=1),
    db.Column("preco_unitario_orcado", db.Float, nullable=False)
)

orcamento_servico = db.Table("orcamento_servico",
    db.Column("orcamento_id", db.Integer, db.ForeignKey("orcamentos.id"), primary_key=True),
    db.Column("servico_id", db.Integer, db.ForeignKey("servicos.id"), primary_key=True),
    db.Column("preco_orcado", db.Float, nullable=False)
)

class Orcamento(db.Model):
    __tablename__ = "orcamentos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_validade = db.Column(db.DateTime, nullable=True)
    descricao_geral = db.Column(db.Text, nullable=True)
    termos_condicoes = db.Column(db.Text, nullable=True)
    valor_total_orcado = db.Column(db.Float, nullable=True, default=0.0)
    status = db.Column(db.String(50), nullable=False, default="pendente")  # pendente, aprovado, reprovado, enviado
    # Se o orçamento for convertido em OS
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey("ordens_de_servico.id"), nullable=True)

    cliente = db.relationship("Cliente", backref=db.backref("orcamentos", lazy="dynamic"))
    produtos_orcados = db.relationship("Produto", secondary=orcamento_produto, lazy="subquery",
                                     backref=db.backref("orcamentos_associados", lazy=True))
    servicos_orcados = db.relationship("Servico", secondary=orcamento_servico, lazy="subquery",
                                     backref=db.backref("orcamentos_associados", lazy=True))

    def __init__(self, **kwargs):
        super(Orcamento, self).__init__(**kwargs)
        if not self.data_validade:
            self.data_validade = datetime.utcnow() + timedelta(days=30) # Padrão de 30 dias de validade

    def calcular_valor_total(self):
        total = 0.0
        # Produtos
        for item_produto in db.session.query(orcamento_produto).filter_by(orcamento_id=self.id).all():
            total += item_produto.quantidade * item_produto.preco_unitario_orcado
        # Serviços
        for item_servico in db.session.query(orcamento_servico).filter_by(orcamento_id=self.id).all():
            total += item_servico.preco_orcado
        self.valor_total_orcado = total
        return total

    def to_dict(self):
        produtos = []
        for item_produto_assoc in db.session.query(orcamento_produto).filter_by(orcamento_id=self.id).all():
            produto_obj = db.session.query(Produto).get(item_produto_assoc.produto_id)
            produtos.append({
                "produto_id": item_produto_assoc.produto_id,
                "nome": produto_obj.descricao if produto_obj else "N/A",
                "quantidade": item_produto_assoc.quantidade,
                "preco_unitario_orcado": item_produto_assoc.preco_unitario_orcado,
                "subtotal": item_produto_assoc.quantidade * item_produto_assoc.preco_unitario_orcado
            })
        
        servicos = []
        for item_servico_assoc in db.session.query(orcamento_servico).filter_by(orcamento_id=self.id).all():
            servico_obj = db.session.query(Servico).get(item_servico_assoc.servico_id)
            servicos.append({
                "servico_id": item_servico_assoc.servico_id,
                "nome": servico_obj.nome if servico_obj else "N/A",
                "preco_orcado": item_servico_assoc.preco_orcado
            })

        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente.nome if self.cliente else None,
            "data_criacao": self.data_criacao.isoformat(),
            "data_validade": self.data_validade.isoformat() if self.data_validade else None,
            "descricao_geral": self.descricao_geral,
            "termos_condicoes": self.termos_condicoes,
            "valor_total_orcado": self.valor_total_orcado,
            "status": self.status,
            "ordem_servico_id": self.ordem_servico_id,
            "produtos_orcados": produtos,
            "servicos_orcados": servicos
        }

