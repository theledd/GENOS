from flask import Blueprint, request, jsonify
from src.models.link_util import LinkUtil
from src.models.user import db
from datetime import datetime

link_util_bp = Blueprint("link_util_bp", __name__)

@link_util_bp.route("/links-uteis", methods=["POST"])
def create_link_util():
    data = request.get_json()
    if not data or not data.get("titulo") or not data.get("url"):
        return jsonify({"message": "Título e URL do link são obrigatórios"}), 400

    novo_link = LinkUtil(
        titulo=data.get("titulo"),
        url=data.get("url"),
        descricao=data.get("descricao"),
        categoria=data.get("categoria")
    )

    try:
        db.session.add(novo_link)
        db.session.commit()
        return jsonify(novo_link.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar link útil", "error": str(e)}), 500

@link_util_bp.route("/links-uteis", methods=["GET"])
def get_all_links_uteis():
    try:
        categoria_filter = request.args.get("categoria")
        query = LinkUtil.query.order_by(LinkUtil.data_criacao.desc())
        if categoria_filter:
            query = query.filter(LinkUtil.categoria.ilike(f"%{categoria_filter}%")) # Case-insensitive search
        
        links = query.all()
        return jsonify([link.to_dict() for link in links]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar links úteis", "error": str(e)}), 500

@link_util_bp.route("/links-uteis/<int:link_id>", methods=["GET"])
def get_link_util(link_id):
    try:
        link = LinkUtil.query.get(link_id)
        if link:
            return jsonify(link.to_dict()), 200
        return jsonify({"message": "Link útil não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar link útil", "error": str(e)}), 500

@link_util_bp.route("/links-uteis/<int:link_id>", methods=["PUT"])
def update_link_util(link_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        link = LinkUtil.query.get(link_id)
        if not link:
            return jsonify({"message": "Link útil não encontrado"}), 404

        link.titulo = data.get("titulo", link.titulo)
        link.url = data.get("url", link.url)
        link.descricao = data.get("descricao", link.descricao)
        link.categoria = data.get("categoria", link.categoria)

        db.session.commit()
        return jsonify(link.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar link útil", "error": str(e)}), 500

@link_util_bp.route("/links-uteis/<int:link_id>", methods=["DELETE"])
def delete_link_util(link_id):
    try:
        link = LinkUtil.query.get(link_id)
        if not link:
            return jsonify({"message": "Link útil não encontrado"}), 404

        db.session.delete(link)
        db.session.commit()
        return jsonify({"message": "Link útil excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir link útil", "error": str(e)}), 500

