from flask import Blueprint, request, jsonify
from src.models.produto import Produto
from src.models.user import db

produto_bp = Blueprint("produto_bp", __name__)

@produto_bp.route("/produtos", methods=["POST"])
def create_produto():
    data = request.get_json()
    if not data or not data.get("descricao") or data.get("preco_venda") is None:
        return jsonify({"message": "Descrição e preço de venda do produto são obrigatórios"}), 400
    
    novo_produto = Produto(
        codigo_barra=data.get("codigo_barra"),
        descricao=data.get("descricao"),
        tipo_movimento=data.get("tipo_movimento"),
        preco_compra=data.get("preco_compra"),
        preco_venda=data.get("preco_venda"),
        unidade=data.get("unidade"),
        estoque=data.get("estoque", 0)
    )
    try:
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify(novo_produto.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar produto", "error": str(e)}), 500

@produto_bp.route("/produtos", methods=["GET"])
def get_produtos():
    try:
        produtos = Produto.query.all()
        return jsonify([produto.to_dict() for produto in produtos]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar produtos", "error": str(e)}), 500

@produto_bp.route("/produtos/<int:produto_id>", methods=["GET"])
def get_produto(produto_id):
    try:
        produto = Produto.query.get(produto_id)
        if produto:
            return jsonify(produto.to_dict()), 200
        return jsonify({"message": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar produto", "error": str(e)}), 500

@produto_bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def update_produto(produto_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"message": "Produto não encontrado"}), 404

        produto.codigo_barra = data.get("codigo_barra", produto.codigo_barra)
        produto.descricao = data.get("descricao", produto.descricao)
        produto.tipo_movimento = data.get("tipo_movimento", produto.tipo_movimento)
        produto.preco_compra = data.get("preco_compra", produto.preco_compra)
        produto.preco_venda = data.get("preco_venda", produto.preco_venda)
        produto.unidade = data.get("unidade", produto.unidade)
        produto.estoque = data.get("estoque", produto.estoque)

        db.session.commit()
        return jsonify(produto.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar produto", "error": str(e)}), 500

@produto_bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def delete_produto(produto_id):
    try:
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"message": "Produto não encontrado"}), 404

        db.session.delete(produto)
        db.session.commit()
        return jsonify({"message": "Produto excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir produto", "error": str(e)}), 500

