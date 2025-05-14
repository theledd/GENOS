from flask import Blueprint, jsonify, Response
from src.models.ordem_servico import OrdemDeServico
from src.models.cliente import Cliente
from fpdf import FPDF

etiqueta_bp = Blueprint("etiqueta_bp", __name__)

class PDFLabel(FPDF):
    def header(self):
        pass # No header for labels

    def footer(self):
        pass # No footer for labels

    def create_label_content(self, os_numero, cliente_nome, equipamento_desc, data_entrada):
        self.add_page(orientation="L", format=(50, 80)) # Landscape, 80mm width, 50mm height (adjust as needed)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"OS: {os_numero}", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 7, f"Cliente: {cliente_nome}", 0, "L")
        self.multi_cell(0, 7, f"Equip.: {equipamento_desc[:50]}", 0, "L") # Truncate description if too long
        self.set_font("Arial", "", 8)
        self.cell(0, 7, f"Entrada: {data_entrada}", 0, 1, "L")

@etiqueta_bp.route("/os/<int:os_id>/etiqueta", methods=["GET"])
def gerar_etiqueta_os(os_id):
    try:
        os_item = OrdemDeServico.query.get(os_id)
        if not os_item:
            return jsonify({"message": "Ordem de Serviço não encontrada"}), 404

        if not os_item.cliente:
            return jsonify({"message": "Cliente não associado a esta OS"}), 404

        pdf = PDFLabel()
        os_numero = str(os_item.id).zfill(6) # Pad OS number with zeros
        cliente_nome = os_item.cliente.nome
        # Usando descricao_problema como placeholder para descrição do equipamento
        # Idealmente, a OS teria um campo específico para "Equipamento"
        equipamento_desc = os_item.descricao_problema 
        data_entrada_str = os_item.data_entrada.strftime("%d/%m/%Y") if os_item.data_entrada else "N/A"

        pdf.create_label_content(os_numero, cliente_nome, equipamento_desc, data_entrada_str)
        
        response_content = pdf.output(dest="S").encode("latin-1") # Output as bytes
        
        return Response(response_content,
                        mimetype="application/pdf",
                        headers={"Content-Disposition": f"attachment;filename=etiqueta_os_{os_numero}.pdf"})

    except Exception as e:
        return jsonify({"message": "Erro ao gerar etiqueta", "error": str(e)}), 500

