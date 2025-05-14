from flask import Blueprint, request, jsonify
from src.models.ordem_servico import OrdemDeServico, ordem_servico_produto, ordem_servico_servico
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.models.servico import Servico
from src.models.user import db
from datetime import datetime

os_bp = Blueprint("os_bp", __name__)

@os_bp.route("/os", methods=["POST"])
def create_os():
    data = request.get_json()
    if not data or not data.get("cliente_id") or not data.get("descricao_problema"):
        return jsonify({"message": "ID do Cliente e Descrição do Problema são obrigatórios"}), 400

    cliente = Cliente.query.get(data.get("cliente_id"))
    if not cliente:
        return jsonify({"message": "Cliente não encontrado"}), 404

    nova_os = OrdemDeServico(
        cliente_id=data.get("cliente_id"),
        data_entrada=datetime.utcnow(),
        data_finalizacao_prevista=datetime.fromisoformat(data.get("data_finalizacao_prevista")) if data.get("data_finalizacao_prevista") else None,
        descricao_problema=data.get("descricao_problema"),
        diagnostico_tecnico=data.get("diagnostico_tecnico"),
        solucao_aplicada=data.get("solucao_aplicada"),
        status=data.get("status", "Orçamento"),
        observacoes=data.get("observacoes")
    )

    # Lógica para adicionar produtos e serviços será em rotas separadas ou aqui com mais complexidade
    # Por enquanto, focamos na criação da OS básica
    # Os totais serão calculados ao adicionar/remover itens
    nova_os.calcular_totais() 

    try:
        db.session.add(nova_os)
        db.session.commit()
        return jsonify(nova_os.to_dict(include_details=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar Ordem de Serviço", "error": str(e)}), 500

@os_bp.route("/os", methods=["GET"])
def get_all_os():
    try:
        lista_os = OrdemDeServico.query.order_by(OrdemDeServico.data_entrada.desc()).all()
        return jsonify([os_item.to_dict(include_details=True) for os_item in lista_os]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar Ordens de Serviço", "error": str(e)}), 500

@os_bp.route("/os/<int:os_id>", methods=["GET"])
def get_os(os_id):
    try:
        os_item = OrdemDeServico.query.get(os_id)
        if os_item:
            return jsonify(os_item.to_dict(include_details=True)), 200
        return jsonify({"message": "Ordem de Serviço não encontrada"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar Ordem de Serviço", "error": str(e)}), 500

@os_bp.route("/os/<int:os_id>", methods=["PUT"])
def update_os(os_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        os_item = OrdemDeServico.query.get(os_id)
        if not os_item:
            return jsonify({"message": "Ordem de Serviço não encontrada"}), 404

        os_item.cliente_id = data.get("cliente_id", os_item.cliente_id)
        # data_entrada não deve ser alterada usualmente após criação
        if data.get("data_finalizacao_prevista"):
             os_item.data_finalizacao_prevista = datetime.fromisoformat(data.get("data_finalizacao_prevista"))
        if data.get("data_finalizacao_real"):
            os_item.data_finalizacao_real = datetime.fromisoformat(data.get("data_finalizacao_real"))
        
        os_item.descricao_problema = data.get("descricao_problema", os_item.descricao_problema)
        os_item.diagnostico_tecnico = data.get("diagnostico_tecnico", os_item.diagnostico_tecnico)
        os_item.solucao_aplicada = data.get("solucao_aplicada", os_item.solucao_aplicada)
        os_item.status = data.get("status", os_item.status)
        os_item.observacoes = data.get("observacoes", os_item.observacoes)
        
        # A atualização de produtos e serviços associados e o recálculo de totais
        # seriam feitos aqui ou em endpoints dedicados.
        os_item.calcular_totais() # Recalcula totais caso valores base mudem

        db.session.commit()
        return jsonify(os_item.to_dict(include_details=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar Ordem de Serviço", "error": str(e)}), 500

@os_bp.route("/os/<int:os_id>", methods=["DELETE"])
def delete_os(os_id):
    try:
        os_item = OrdemDeServico.query.get(os_id)
        if not os_item:
            return jsonify({"message": "Ordem de Serviço não encontrada"}), 404
        
        # Remover associações antes de deletar a OS
        # Isso é importante para integridade referencial se não houver cascade delete configurado no DB
        # Exemplo para produtos (similar para serviços):
        # DELETE FROM ordem_servico_produto WHERE ordem_servico_id = :os_id
        stmt_produtos = ordem_servico_produto.delete().where(ordem_servico_produto.c.ordem_servico_id == os_id)
        db.session.execute(stmt_produtos)
        stmt_servicos = ordem_servico_servico.delete().where(ordem_servico_servico.c.ordem_servico_id == os_id)
        db.session.execute(stmt_servicos)

        db.session.delete(os_item)
        db.session.commit()
        return jsonify({"message": "Ordem de Serviço excluída com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir Ordem de Serviço", "error": str(e)}), 500

# --- Rotas para adicionar/remover produtos e serviços de uma OS ---

@os_bp.route("/os/<int:os_id>/produtos", methods=["POST"])
def add_produto_to_os(os_id):
    data = request.get_json()
    if not data or not data.get("produto_id") or data.get("quantidade") is None or data.get("preco_unitario_cobrado") is None:
        return jsonify({"message": "ID do Produto, Quantidade e Preço Unitário Cobrado são obrigatórios"}), 400

    os_item = OrdemDeServico.query.get(os_id)
    if not os_item:
        return jsonify({"message": "Ordem de Serviço não encontrada"}), 404

    produto = Produto.query.get(data.get("produto_id"))
    if not produto:
        return jsonify({"message": "Produto não encontrado"}), 404

    try:
        # Adiciona o produto à OS através da tabela de associação
        # Verifica se o produto já está na OS para evitar duplicatas ou atualizar quantidade
        # Esta é uma forma simplificada. Uma forma mais robusta verificaria se a linha já existe.
        insert_stmt = ordem_servico_produto.insert().values(
            ordem_servico_id=os_id,
            produto_id=data.get("produto_id"),
            quantidade=data.get("quantidade"),
            preco_unitario_cobrado=data.get("preco_unitario_cobrado")
        )
        db.session.execute(insert_stmt)
        
        # Atualiza o valor total de produtos na OS
        os_item.valor_total_produtos = (os_item.valor_total_produtos or 0.0) + (data.get("quantidade") * data.get("preco_unitario_cobrado"))
        os_item.calcular_totais()
        
        db.session.commit()
        return jsonify(os_item.to_dict(include_details=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao adicionar produto à OS", "error": str(e)}), 500

@os_bp.route("/os/<int:os_id>/servicos", methods=["POST"])
def add_servico_to_os(os_id):
    data = request.get_json()
    if not data or not data.get("servico_id") or data.get("preco_cobrado") is None:
        return jsonify({"message": "ID do Serviço e Preço Cobrado são obrigatórios"}), 400

    os_item = OrdemDeServico.query.get(os_id)
    if not os_item:
        return jsonify({"message": "Ordem de Serviço não encontrada"}), 404

    servico = Servico.query.get(data.get("servico_id"))
    if not servico:
        return jsonify({"message": "Serviço não encontrado"}), 404

    try:
        insert_stmt = ordem_servico_servico.insert().values(
            ordem_servico_id=os_id,
            servico_id=data.get("servico_id"),
            preco_cobrado=data.get("preco_cobrado")
        )
        db.session.execute(insert_stmt)

        os_item.valor_total_servicos = (os_item.valor_total_servicos or 0.0) + data.get("preco_cobrado")
        os_item.calcular_totais()

        db.session.commit()
        return jsonify(os_item.to_dict(include_details=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao adicionar serviço à OS", "error": str(e)}), 500

# Rotas para remover produtos/serviços de uma OS podem ser implementadas de forma similar (DELETE)
# Ex: /os/<int:os_id>/produtos/<int:produto_id>
# Ex: /os/<int:os_id>/servicos/<int:servico_id>

