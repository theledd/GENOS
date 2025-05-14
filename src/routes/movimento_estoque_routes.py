from flask import Blueprint, request, jsonify
from src.models.movimento_estoque import MovimentoEstoque
from src.models.produto import Produto
from src.models.user import db
from datetime import datetime

movimento_estoque_bp = Blueprint("movimento_estoque_bp", __name__)

@movimento_estoque_bp.route("/estoque/movimentos", methods=["POST"])
def create_movimento_estoque():
    data = request.get_json()
    if not data or not data.get("produto_id") or not data.get("tipo") or data.get("quantidade") is None:
        return jsonify({"message": "ID do Produto, Tipo de Movimento e Quantidade são obrigatórios"}), 400

    produto = Produto.query.get(data.get("produto_id"))
    if not produto:
        return jsonify({"message": "Produto não encontrado"}), 404

    quantidade = data.get("quantidade")
    tipo = data.get("tipo").lower()

    if tipo not in ["entrada", "saida", "ajuste_entrada", "ajuste_saida"]:
        return jsonify({"message": "Tipo de movimento inválido. Use 'entrada', 'saida', 'ajuste_entrada' ou 'ajuste_saida'."}), 400
    
    if quantidade <= 0:
        return jsonify({"message": "Quantidade deve ser um número positivo."}), 400

    novo_movimento = MovimentoEstoque(
        produto_id=data.get("produto_id"),
        tipo=tipo,
        quantidade=quantidade,
        data_movimento=datetime.utcnow(),
        observacao=data.get("observacao")
        # Adicionar ordem_servico_id ou compra_id se necessário no futuro
    )

    try:
        # Atualizar o estoque do produto
        if tipo == "entrada" or tipo == "ajuste_entrada":
            produto.estoque += quantidade
        elif tipo == "saida" or tipo == "ajuste_saida":
            if produto.estoque < quantidade:
                return jsonify({"message": f"Estoque insuficiente para o produto {produto.descricao}. Estoque atual: {produto.estoque}"}), 400
            produto.estoque -= quantidade
        
        db.session.add(novo_movimento)
        db.session.add(produto) # Adiciona a instância do produto para salvar a alteração no estoque
        db.session.commit()
        return jsonify(novo_movimento.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar movimento de estoque", "error": str(e)}), 500

@movimento_estoque_bp.route("/estoque/movimentos", methods=["GET"])
def get_all_movimentos_estoque():
    try:
        # Adicionar filtros por produto_id, tipo, data, etc. como query params se necessário
        produto_id_filter = request.args.get("produto_id", type=int)
        
        query = MovimentoEstoque.query.order_by(MovimentoEstoque.data_movimento.desc())
        
        if produto_id_filter:
            query = query.filter(MovimentoEstoque.produto_id == produto_id_filter)
            
        movimentos = query.all()
        return jsonify([movimento.to_dict() for movimento in movimentos]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar movimentos de estoque", "error": str(e)}), 500

@movimento_estoque_bp.route("/estoque/movimentos/<int:movimento_id>", methods=["GET"])
def get_movimento_estoque(movimento_id):
    try:
        movimento = MovimentoEstoque.query.get(movimento_id)
        if movimento:
            return jsonify(movimento.to_dict()), 200
        return jsonify({"message": "Movimento de estoque não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar movimento de estoque", "error": str(e)}), 500

# Geralmente, movimentos de estoque não são atualizados ou deletados para manter a integridade do histórico.
# Se for necessário, implementar com cuidado, considerando o impacto no estoque do produto.
# @movimento_estoque_bp.route("/estoque/movimentos/<int:movimento_id>", methods=["PUT"])
# def update_movimento_estoque(movimento_id):
#     # ... (implementar com cautela)

# @movimento_estoque_bp.route("/estoque/movimentos/<int:movimento_id>", methods=["DELETE"])
# def delete_movimento_estoque(movimento_id):
#     # ... (implementar com cautela, ajustando o estoque do produto de volta)

@movimento_estoque_bp.route("/estoque/alertas", methods=["GET"])
def get_alertas_estoque():
    # Esta rota pode ser expandida para definir limites de estoque mínimo por produto
    # Por agora, vamos retornar produtos com estoque baixo (ex: <= 5, pode ser configurável)
    limite_estoque_baixo = request.args.get("limite", default=5, type=int)
    try:
        produtos_estoque_baixo = Produto.query.filter(Produto.estoque <= limite_estoque_baixo).all()
        return jsonify([produto.to_dict() for produto in produtos_estoque_baixo]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar alertas de estoque", "error": str(e)}), 500

