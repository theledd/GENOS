from flask import Blueprint, request, jsonify
from src.models.cliente import Cliente
from src.models.user import db # Assuming db is initialized in user.py or a central models.py

cliente_bp = Blueprint("cliente_bp", __name__)

@cliente_bp.route("/clientes", methods=["POST"])
def create_cliente():
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"message": "Nome do cliente é obrigatório"}), 400
    
    novo_cliente = Cliente(
        nome=data.get("nome"),
        telefone=data.get("telefone"),
        email=data.get("email"),
        endereco=data.get("endereco"),
        cpf_cnpj=data.get("cpf_cnpj")
    )
    try:
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify(novo_cliente.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar cliente", "error": str(e)}), 500

@cliente_bp.route("/clientes", methods=["GET"])
def get_clientes():
    try:
        clientes = Cliente.query.all()
        return jsonify([cliente.to_dict() for cliente in clientes]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar clientes", "error": str(e)}), 500

@cliente_bp.route("/clientes/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if cliente:
            return jsonify(cliente.to_dict()), 200
        return jsonify({"message": "Cliente não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar cliente", "error": str(e)}), 500

@cliente_bp.route("/clientes/<int:cliente_id>", methods=["PUT"])
def update_cliente(cliente_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"message": "Cliente não encontrado"}), 404

        cliente.nome = data.get("nome", cliente.nome)
        cliente.telefone = data.get("telefone", cliente.telefone)
        cliente.email = data.get("email", cliente.email)
        cliente.endereco = data.get("endereco", cliente.endereco)
        cliente.cpf_cnpj = data.get("cpf_cnpj", cliente.cpf_cnpj)

        db.session.commit()
        return jsonify(cliente.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar cliente", "error": str(e)}), 500

@cliente_bp.route("/clientes/<int:cliente_id>", methods=["DELETE"])
def delete_cliente(cliente_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"message": "Cliente não encontrado"}), 404

        db.session.delete(cliente)
        db.session.commit()
        return jsonify({"message": "Cliente excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir cliente", "error": str(e)}), 500

