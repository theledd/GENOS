from flask import Blueprint, request, jsonify
from src.models.lancamento_financeiro import LancamentoFinanceiro
from src.models.user import db
from datetime import datetime

financeiro_bp = Blueprint("financeiro_bp", __name__)

@financeiro_bp.route("/financeiro/lancamentos", methods=["POST"])
def create_lancamento():
    data = request.get_json()
    if not data or not data.get("descricao") or data.get("valor") is None or not data.get("tipo"):
        return jsonify({"message": "Descrição, Valor e Tipo do lançamento são obrigatórios"}), 400

    tipo = data.get("tipo").lower()
    if tipo not in ["receita", "despesa"]:
        return jsonify({"message": "Tipo de lançamento inválido. Use 'receita' ou 'despesa'."}), 400

    novo_lancamento = LancamentoFinanceiro(
        descricao=data.get("descricao"),
        valor=data.get("valor"),
        tipo=tipo,
        data_lancamento=datetime.utcnow(),
        data_vencimento=datetime.fromisoformat(data.get("data_vencimento")).date() if data.get("data_vencimento") else None,
        data_pagamento_recebimento=datetime.fromisoformat(data.get("data_pagamento_recebimento")).date() if data.get("data_pagamento_recebimento") else None,
        status=data.get("status", "pendente"),
        observacao=data.get("observacao"),
        cliente_id=data.get("cliente_id"),
        ordem_servico_id=data.get("ordem_servico_id")
    )

    try:
        db.session.add(novo_lancamento)
        db.session.commit()
        return jsonify(novo_lancamento.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar lançamento financeiro", "error": str(e)}), 500

@financeiro_bp.route("/financeiro/lancamentos", methods=["GET"])
def get_all_lancamentos():
    try:
        # Adicionar filtros por tipo, status, data, cliente_id, os_id como query params
        tipo_filter = request.args.get("tipo")
        status_filter = request.args.get("status")
        # Adicionar mais filtros conforme necessário
        
        query = LancamentoFinanceiro.query.order_by(LancamentoFinanceiro.data_lancamento.desc())
        
        if tipo_filter:
            query = query.filter(LancamentoFinanceiro.tipo == tipo_filter.lower())
        if status_filter:
            query = query.filter(LancamentoFinanceiro.status == status_filter.lower())
            
        lancamentos = query.all()
        return jsonify([lanc.to_dict() for lanc in lancamentos]), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar lançamentos financeiros", "error": str(e)}), 500

@financeiro_bp.route("/financeiro/lancamentos/<int:lancamento_id>", methods=["GET"])
def get_lancamento(lancamento_id):
    try:
        lancamento = LancamentoFinanceiro.query.get(lancamento_id)
        if lancamento:
            return jsonify(lancamento.to_dict()), 200
        return jsonify({"message": "Lançamento financeiro não encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar lançamento financeiro", "error": str(e)}), 500

@financeiro_bp.route("/financeiro/lancamentos/<int:lancamento_id>", methods=["PUT"])
def update_lancamento(lancamento_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização não fornecidos"}), 400

    try:
        lancamento = LancamentoFinanceiro.query.get(lancamento_id)
        if not lancamento:
            return jsonify({"message": "Lançamento financeiro não encontrado"}), 404

        lancamento.descricao = data.get("descricao", lancamento.descricao)
        lancamento.valor = data.get("valor", lancamento.valor)
        if data.get("tipo"):
            tipo = data.get("tipo").lower()
            if tipo not in ["receita", "despesa"]:
                return jsonify({"message": "Tipo de lançamento inválido."}), 400
            lancamento.tipo = tipo
        if data.get("data_vencimento"):
            lancamento.data_vencimento = datetime.fromisoformat(data.get("data_vencimento")).date()
        if data.get("data_pagamento_recebimento"):
            lancamento.data_pagamento_recebimento = datetime.fromisoformat(data.get("data_pagamento_recebimento")).date()
        lancamento.status = data.get("status", lancamento.status)
        lancamento.observacao = data.get("observacao", lancamento.observacao)
        lancamento.cliente_id = data.get("cliente_id", lancamento.cliente_id)
        lancamento.ordem_servico_id = data.get("ordem_servico_id", lancamento.ordem_servico_id)

        db.session.commit()
        return jsonify(lancamento.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao atualizar lançamento financeiro", "error": str(e)}), 500

@financeiro_bp.route("/financeiro/lancamentos/<int:lancamento_id>", methods=["DELETE"])
def delete_lancamento(lancamento_id):
    try:
        lancamento = LancamentoFinanceiro.query.get(lancamento_id)
        if not lancamento:
            return jsonify({"message": "Lançamento financeiro não encontrado"}), 404

        db.session.delete(lancamento)
        db.session.commit()
        return jsonify({"message": "Lançamento financeiro excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao excluir lançamento financeiro", "error": str(e)}), 500

@financeiro_bp.route("/financeiro/fluxo-caixa", methods=["GET"])
def get_fluxo_caixa():
    # Esta é uma rota simplificada para fluxo de caixa.
    # Pode ser expandida para aceitar filtros de período (data_inicio, data_fim).
    try:
        total_receitas = db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(LancamentoFinanceiro.tipo == "receita", LancamentoFinanceiro.status.in_(["pago", "recebido"]) ).scalar() or 0.0
        total_despesas = db.session.query(db.func.sum(LancamentoFinanceiro.valor)).filter(LancamentoFinanceiro.tipo == "despesa", LancamentoFinanceiro.status == "pago").scalar() or 0.0
        saldo = total_receitas - total_despesas
        
        return jsonify({
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": saldo
        }), 200
    except Exception as e:
        return jsonify({"message": "Erro ao calcular fluxo de caixa", "error": str(e)}), 500

