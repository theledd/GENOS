from flask import Blueprint, jsonify, Response
from src.models.ordem_servico import OrdemDeServico, ordem_servico_produto, ordem_servico_servico
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.models.servico import Servico
from src.models.user import db # Import db for executing raw queries if needed for association tables
from fpdf import FPDF
from datetime import datetime

recibo_bp = Blueprint("recibo_bp", __name__)

class PDFRecibo(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', empresa_nome="Sua Assistência Técnica", empresa_endereco="Seu Endereço", empresa_contato="Seu Contato"):
        super().__init__(orientation, unit, format)
        self.empresa_nome = empresa_nome
        self.empresa_endereco = empresa_endereco
        self.empresa_contato = empresa_contato
        try:
            self.add_font("NotoSansCJK", fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
            self.set_font("NotoSansCJK", size=10)
        except RuntimeError:
            print("Fonte NotoSansCJK não encontrada, usando Arial padrão.")
            self.set_font("Arial", size=10) # Fallback font

    def header(self):
        current_font_family = self.font_family
        current_font_style = self.font_style
        current_font_size = self.font_size_pt
        
        self.set_font(current_font_family, "B", 16)
        self.cell(0, 10, self.empresa_nome, 0, 1, "C")
        self.set_font(current_font_family, "", 10)
        self.cell(0, 5, self.empresa_endereco, 0, 1, "C")
        self.cell(0, 5, self.empresa_contato, 0, 1, "C")
        self.ln(10)
        self.set_font(current_font_family, "B", 18)
        self.cell(0, 10, "RECIBO DE PAGAMENTO", 0, 1, "C")
        self.ln(5)
        self.set_font(current_font_family, current_font_style, current_font_size)

    def footer(self):
        current_font_family = self.font_family
        # current_font_style = self.font_style # Not needed if only changing to Italic
        # current_font_size = self.font_size_pt # Not needed if only changing to Italic
        self.set_y(-15)
        self.set_font(current_font_family, "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

    def recibo_content(self, os_item):
        current_font_family = self.font_family
        self.set_font(current_font_family, "", 12)
        
        self.cell(0, 10, f"Recebemos de: {os_item.cliente.nome if os_item.cliente else 'Cliente não informado'}", 0, 1, "L")
        cpf_cnpj_cliente = os_item.cliente.cpf_cnpj if os_item.cliente and os_item.cliente.cpf_cnpj else "Não informado"
        self.cell(0, 10, f"CPF/CNPJ: {cpf_cnpj_cliente}", 0, 1, "L")
        self.ln(5)
        
        valor_total_texto = f"R$ {os_item.valor_total_os:.2f}" if os_item.valor_total_os is not None else "Valor não calculado"
        self.multi_cell(0, 10, f"A quantia de {valor_total_texto} referente à Ordem de Serviço Nº {str(os_item.id).zfill(6)}.", 0, "L")
        self.ln(5)

        self.set_font(current_font_family, "B", 11)
        self.cell(0, 10, "Detalhes da Ordem de Serviço:", 0, 1, "L")
        self.set_font(current_font_family, "", 10)
        self.multi_cell(0, 7, f"Descrição do Problema: {os_item.descricao_problema}", 0, "L")
        if os_item.diagnostico_tecnico:
            self.multi_cell(0, 7, f"Diagnóstico Técnico: {os_item.diagnostico_tecnico}", 0, "L")
        if os_item.solucao_aplicada:
            self.multi_cell(0, 7, f"Solução Aplicada: {os_item.solucao_aplicada}", 0, "L")
        self.ln(5)

        # Detalhes de Produtos e Serviços
        self.set_font(current_font_family, "B", 10)
        if db.session.query(ordem_servico_produto).filter_by(ordem_servico_id=os_item.id).first():
            self.cell(0, 7, "Produtos Utilizados:", 0, 1, "L")
            self.set_font(current_font_family, "", 9)
            # Query for associated products and their details in the OS
            produtos_na_os = db.session.query(Produto.descricao, ordem_servico_produto.c.quantidade, ordem_servico_produto.c.preco_unitario_cobrado)\
                .join(ordem_servico_produto, Produto.id == ordem_servico_produto.c.produto_id)\
                .filter(ordem_servico_produto.c.ordem_servico_id == os_item.id).all()
            for desc, qtd, preco_unit in produtos_na_os:
                self.cell(0, 6, f"  - {desc} (Qtd: {qtd}, Unit.: R$ {preco_unit:.2f}, Total: R$ {qtd*preco_unit:.2f})", 0, 1, "L")
            self.ln(3)

        if db.session.query(ordem_servico_servico).filter_by(ordem_servico_id=os_item.id).first():
            self.set_font(current_font_family, "B", 10)
            self.cell(0, 7, "Serviços Prestados:", 0, 1, "L")
            self.set_font(current_font_family, "", 9)
            # Query for associated services and their details in the OS
            servicos_na_os = db.session.query(Servico.nome, ordem_servico_servico.c.preco_cobrado)\
                .join(ordem_servico_servico, Servico.id == ordem_servico_servico.c.servico_id)\
                .filter(ordem_servico_servico.c.ordem_servico_id == os_item.id).all()
            for nome_serv, preco_serv in servicos_na_os:
                self.cell(0, 6, f"  - {nome_serv} (Valor: R$ {preco_serv:.2f})", 0, 1, "L")
            self.ln(3)

        self.ln(10)
        self.set_font(current_font_family, "", 10)
        data_emissao = datetime.now().strftime("%d de %B de %Y") # Formato por extenso
        self.cell(0, 10, f"Local e Data de Emissão: _______________, {data_emissao}", 0, 1, "L")
        self.ln(15)
        self.cell(0, 10, "___________________________________", 0, 1, "C")
        self.cell(0, 5, self.empresa_nome, 0, 1, "C")

@recibo_bp.route("/os/<int:os_id>/recibo", methods=["GET"])
def gerar_recibo_os(os_id):
    try:
        os_item = OrdemDeServico.query.get(os_id)
        if not os_item:
            return jsonify({"message": "Ordem de Serviço não encontrada"}), 404

        # Você pode buscar os dados da empresa de um arquivo de configuração ou do banco de dados
        pdf = PDFRecibo(empresa_nome="Minha Assistência Técnica Top", 
                        empresa_endereco="Rua das Palmeiras, 123 - Centro", 
                        empresa_contato="(XX) YYYYY-ZZZZ | email@exemplo.com")
        pdf.add_page()
        pdf.recibo_content(os_item)
        
        response_content = pdf.output(dest="S").encode("latin-1")
        
        return Response(response_content,
                        mimetype="application/pdf",
                        headers={"Content-Disposition": f"attachment;filename=recibo_os_{str(os_item.id).zfill(6)}.pdf"})

    except Exception as e:
        print(f"Erro ao gerar recibo: {e}") # Log do erro no servidor
        return jsonify({"message": "Erro ao gerar recibo", "error": str(e)}), 500

