from src.models.user import db
from datetime import datetime

# Tabela de associação para Ordens de Serviço e Produtos (Muitos-para-Muitos)
ordem_servico_produto = db.Table('ordem_servico_produto',
    db.Column('ordem_servico_id', db.Integer, db.ForeignKey('ordens_de_servico.id'), primary_key=True),
    db.Column('produto_id', db.Integer, db.ForeignKey('produtos.id'), primary_key=True),
    db.Column('quantidade', db.Integer, nullable=False, default=1),
    db.Column('preco_unitario_cobrado', db.Float, nullable=False)
)

# Tabela de associação para Ordens de Serviço e Serviços (Muitos-para-Muitos)
ordem_servico_servico = db.Table('ordem_servico_servico',
    db.Column('ordem_servico_id', db.Integer, db.ForeignKey('ordens_de_servico.id'), primary_key=True),
    db.Column('servico_id', db.Integer, db.ForeignKey('servicos.id'), primary_key=True),
    db.Column('preco_cobrado', db.Float, nullable=False) # Preço do serviço no momento da OS
)

class OrdemDeServico(db.Model):
    __tablename__ = "ordens_de_servico"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_entrada = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_finalizacao_prevista = db.Column(db.DateTime, nullable=True)
    data_finalizacao_real = db.Column(db.DateTime, nullable=True)
    descricao_problema = db.Column(db.Text, nullable=False)
    diagnostico_tecnico = db.Column(db.Text, nullable=True)
    solucao_aplicada = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Orçamento') # Ex: Orçamento, Aguardando Aprovação, Em Andamento, Concluído, Cancelado
    valor_total_servicos = db.Column(db.Float, nullable=True, default=0.0)
    valor_total_produtos = db.Column(db.Float, nullable=True, default=0.0)
    valor_total_os = db.Column(db.Float, nullable=True, default=0.0)
    observacoes = db.Column(db.Text, nullable=True)

    # Relacionamento com Cliente (Um-para-Muitos: Um cliente pode ter várias OS)
    cliente = db.relationship('Cliente', backref=db.backref('ordens_de_servico', lazy=True))

    # Relacionamento Muitos-para-Muitos com Produtos
    produtos_associados = db.relationship('Produto', secondary=ordem_servico_produto,
                                lazy='subquery', backref=db.backref('ordens_de_servico_onde_usado', lazy=True))

    # Relacionamento Muitos-para-Muitos com Serviços
    servicos_prestados = db.relationship('Servico', secondary=ordem_servico_servico,
                                 lazy='subquery', backref=db.backref('ordens_de_servico_onde_realizado', lazy=True))

    def __repr__(self):
        return f'<OrdemDeServico {self.id} - Cliente {self.cliente_id}>'

    def calcular_totais(self):
        # Esta função será chamada antes de salvar ou quando itens forem adicionados/removidos
        # Para isso, precisaremos acessar os itens das tabelas de associação
        # Por enquanto, vamos deixar os valores como estão ou zerados
        # A lógica de cálculo será implementada nas rotas ao adicionar/atualizar produtos/serviços na OS
        self.valor_total_os = (self.valor_total_servicos or 0.0) + (self.valor_total_produtos or 0.0)

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'data_finalizacao_prevista': self.data_finalizacao_prevista.isoformat() if self.data_finalizacao_prevista else None,
            'data_finalizacao_real': self.data_finalizacao_real.isoformat() if self.data_finalizacao_real else None,
            'descricao_problema': self.descricao_problema,
            'diagnostico_tecnico': self.diagnostico_tecnico,
            'solucao_aplicada': self.solucao_aplicada,
            'status': self.status,
            'valor_total_servicos': self.valor_total_servicos,
            'valor_total_produtos': self.valor_total_produtos,
            'valor_total_os': self.valor_total_os,
            'observacoes': self.observacoes
        }
        if include_details and self.cliente:
            data['cliente'] = self.cliente.to_dict()
        # Adicionar produtos e serviços associados se include_details for True
        # if include_details:
        #     data['produtos_associados'] = [p.to_dict() for p in self.produtos_associados]
        #     data['servicos_prestados'] = [s.to_dict() for s in self.servicos_prestados]
        return data

