from src.models.user import db
from datetime import datetime

class LancamentoFinanceiro(db.Model):
    __tablename__ = "lancamentos_financeiros"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # "receita", "despesa"
    data_lancamento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_vencimento = db.Column(db.Date, nullable=True)
    data_pagamento_recebimento = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pendente") # "pendente", "pago", "recebido", "vencido"
    observacao = db.Column(db.Text, nullable=True)
    # Opcional: relacionar com Cliente, Fornecedor, OrdemDeServico
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    # fornecedor_id = db.Column(db.Integer, db.ForeignKey("fornecedores.id"), nullable=True) # Se houver
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey("ordens_de_servico.id"), nullable=True)

    cliente = db.relationship("Cliente", backref=db.backref("lancamentos_financeiros", lazy="dynamic"))
    ordem_servico = db.relationship("OrdemDeServico", backref=db.backref("lancamentos_financeiros", lazy="dynamic"))

    def __repr__(self):
        return f"<LancamentoFinanceiro {self.id} - {self.tipo} - {self.valor}>"

    def to_dict(self):
        return {
            "id": self.id,
            "descricao": self.descricao,
            "valor": self.valor,
            "tipo": self.tipo,
            "data_lancamento": self.data_lancamento.isoformat(),
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "data_pagamento_recebimento": self.data_pagamento_recebimento.isoformat() if self.data_pagamento_recebimento else None,
            "status": self.status,
            "observacao": self.observacao,
            "cliente_id": self.cliente_id,
            "ordem_servico_id": self.ordem_servico_id,
            "cliente_nome": self.cliente.nome if self.cliente else None,
        }
