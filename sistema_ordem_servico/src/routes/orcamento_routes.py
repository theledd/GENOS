from flask import Blueprint, request, jsonify, Response
from src.models.orcamento import Orcamento, orcamento_produto, orcamento_servico
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.models.servico import Servico
from src.models.user import db
from fpdf import FPDF
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  # Use Agg backend for Matplotlib to avoid GUI issues
import matplotlib.pyplot as plt
import io

orcamento_bp = Blueprint("orcamento_bp", __name__)

class PDFOrcamento(FPDF):
    def __init__(self, orientation=\'P\', unit=\'mm\', format=\'A4\
                 , empresa_nome="Sua Assistência Técnica", 
                 empresa_endereco="Seu Endereço", 
                 empresa_contato="Seu Contato"):
        super().__init__(orientation, unit, format)
        self.empresa_nome = empresa_nome
        self.empresa_endereco = empresa_endereco
        self.empresa_contato = empresa_contato
        try:
            self.add_font("NotoSansCJK", fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
            self.set_font("NotoSansCJK", size=10)
        except RuntimeError:
            print("Fonte NotoSansCJK não encontrada, usando Arial padrão.")
            self.set_font("Arial", size=10)

    def header(self):
        current_font_family = self.font_family
        self.set_font(current_font_family, "B", 16)
        self.cell(0, 10, self.empresa_nome, 0, 1, "C")
        self.set_font(current_font_family, "", 10)
        self.cell(0, 5, self.empresa_endereco, 0, 1, "C")
        self.cell(0, 5, self.empresa_contato, 0, 1, "C")
        self.ln(10)
        self.set_font(current_font_family, "B", 18)
        self.cell(0, 10, "ORÇAMENTO", 0, 1, "C")
        self.ln(5)
        self.set_font(current_font_family, "", 10) # Reset to default body font

    def footer(self):
        current_font_family = self.font_family
        self.set_y(-15)
        self.set_font(current_font_family, "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

    def orcamento_content(self, orcamento_item):
        current_font_family = self.font_family
        self.set_font(current_font_family, "", 11)

        self.cell(0, 7, f"Orçamento Nº: {str(orcamento_item.id).zfill(6)}", 0, 1, "L")
        self.cell(0, 7, f"Data de Criação: {orcamento_item.data_criacao.strftime("%d/%m/%Y")}", 0, 1, "L")
        self.cell(0, 7, f"Validade: {orcamento_item.data_validade.strftime("%d/%m/%Y") if orcamento_item.data_validade else \'N/A\'}", 0, 1, "L")
        self.ln(5)

        self.set_font(current_font_family, "B", 11)
        self.cell(0, 7, "Cliente:", 0, 1, "L")
        self.set_font(current_font_family, "", 10)
        self.cell(0, 6, f"  Nome: {orcamento_item.cliente.nome if orcamento_item.cliente else \'N/A\'}", 0, 1, "L")
        self.cell(0, 6, f"  CPF/CNPJ: {orcamento_item.cliente.cpf_cnpj if orcamento_item.cliente and orcamento_item.cliente.cpf_cnpj else \'N/A\'}", 0, 1, "L")
        self.cell(0, 6, f"  Telefone: {orcamento_item.cliente.telefone if orcamento_item.cliente and orcamento_item.cliente.telefone else \'N/A\'}", 0, 1, "L")
        self.ln(5)

        if orcamento_item.descricao_geral:
            self.set_font(current_font_family, "B", 11)
            self.cell(0, 7, "Descrição Geral do Serviço/Projeto:", 0, 1, "L")
            self.set_font(current_font_family, "", 10)
            self.multi_cell(0, 6, orcamento_item.descricao_geral, 0, "L")
            self.ln(5)

        self.set_font(current_font_family, "B", 11)
        self.cell(0, 7, "Itens do Orçamento:", 0, 1, "L")
        self.set_font(current_font_family, "B", 10)
        self.cell(100, 7, "Descrição", 1, 0, "C")
        self.cell(30, 7, "Qtd.", 1, 0, "C")
        self.cell(30, 7, "Vlr. Unit.", 1, 0, "C")
        self.cell(30, 7, "Subtotal", 1, 1, "C")
        self.set_font(current_font_family, "", 9)

        itens_orcamento_data = []

        # Produtos
        produtos_na_orc = db.session.query(Produto.descricao, orcamento_produto.c.quantidade, orcamento_produto.c.preco_unitario_orcado)\
            .join(orcamento_produto, Produto.id == orcamento_produto.c.produto_id)\
            .filter(orcamento_produto.c.orcamento_id == orcamento_item.id).all()
        for desc, qtd, preco_unit in produtos_na_orc:
            subtotal = qtd * preco_unit
            self.cell(100, 6, desc, 1, 0, "L")
            self.cell(30, 6, str(qtd), 1, 0, "R")
            self.cell(30, 6, f"R$ {preco_unit:.2f}", 1, 0, "R")
            self.cell(30, 6, f"R$ {subtotal:.2f}", 1, 1, "R")
            itens_orcamento_data.append({"label": desc, "value": subtotal, "type": "Produto"})

        # Serviços
        servicos_na_orc = db.session.query(Servico.nome, orcamento_servico.c.preco_orcado)\
            .join(orcamento_servico, Servico.id == orcamento_servico.c.servico_id)\
            .filter(orcamento_servico.c.orcamento_id == orcamento_item.id).all()
        for nome_serv, preco_serv in servicos_na_orc:
            self.cell(100, 6, nome_serv, 1, 0, "L")
            self.cell(30, 6, "1", 1, 0, "R") # Quantidade para serviço é geralmente 1
            self.cell(30, 6, f"R$ {preco_serv:.2f}", 1, 0, "R")
            self.cell(30, 6, f"R$ {preco_serv:.2f}", 1, 1, "R")
            itens_orcamento_data.append({"label": nome_serv, "value": preco_serv, "type": "Serviço"})
        self.ln(5)

        self.set_font(current_font_family, "B", 12)
        self.cell(160, 8, "Valor Total do Orçamento:", 1, 0, "R")
        self.cell(30, 8, f"R$ {orcamento_item.valor_total_orcado:.2f}", 1, 1, "R")
        self.ln(10)

        # Gerar e adicionar gráfico de pizza
        if itens_orcamento_data:
            labels = [item["label"] for item in itens_orcamento_data]
            sizes = [item["value"] for item in itens_orcamento_data]
            
            fig, ax = plt.subplots(figsize=(6,4))
            ax.pie(sizes, labels=labels, autopct=\'%1.1f%%\', startangle=90, textprops={\'fontsize\': 8})
            ax.axis(\'equal\')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title("Composição do Orçamento", fontsize=10)
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format=\'pngocytes.py
