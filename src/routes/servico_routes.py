from flask import Blueprint, request, jsonify
from src.models.servico import Servico
from src.models.user import db

servico_bp = Blueprint("servico_bp", __name__)

@servico_bp.route("/servicos", methods=["POST"])
def create_servico():
    data = request.get_json()
    if not data or not data.get("nome") or data.get("preco") is None:
        return jsonify({"message": "Nome e preço do serviço são obrigatórios"}), 400
    
    novo_servico = Servico(
        nome=data.get("nome"),
        descricao=data.get("descricao"),
        preco=data.get("preco"),
        tempo_estimado_horas=data.get("tempo_estimado_horas")
    )
    try:
        db.session.add(novo_servico)
        db.session.commit()
        return jsonify(novo_servico.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar serviço", "error": str(e)}), 500

@servico_bp.route("/servicos", methods=["GET"])
def get_servicos():
    try:
        servicos = Servico.query.all()
        return jsonify([servico.to_dict() for servico in servicos]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar serviços", "error": str(e)}), 500

@servico_bp.route("/servicos/<int:servico_id>", methods=["GET"])
def get_servico(servico_id):
    try:
        servico = Servico.query.get(servico_id)
        if servico:
            return jsonify(servico.to_dict()), 200
        return jsonify({"message": "Serviço não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar serviço", "error": str(e)}), 500

@servico_bp.route("/servicos/<int:servico_id>", methods=["PUT"])
def update_servico(servico_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({"message": "Serviço não encontrado"}), 404

        servico.nome = data.get("nome", servico.nome)
        servico.descricao = data.get("descricao", servico.descricao)
        servico.preco = data.get("preco", servico.preco)
        servico.tempo_estimado_horas = data.get("tempo_estimado_horas", servico.tempo_estimado_horas)

        db.session.commit()
        return jsonify(servico.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar serviço", "error": str(e)}), 500

@servico_bp.route("/servicos/<int:servico_id>", methods=["DELETE"])
def delete_servico(servico_id):
    try:
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({"message": "Serviço não encontrado"}), 404

        db.session.delete(servico)
        db.session.commit()
        return jsonify({"message": "Serviço excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir serviço", "error": str(e)}), 500

