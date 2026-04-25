"""Agente de Histórico — consolida dados dos últimos 7 dias."""
import json
from datetime import date, timedelta
from database.db import query
from agents.base_agent import call

SYSTEM = (
    "Você é o Oficial de Dados do Sistema de Marmitas. "
    "Analise o histórico de consumo e retorne um JSON com: "
    "{resumo: string, media_diaria: int, dia_mais_forte: string, "
    "prato_mais_popular: string, taxa_desperdicio_pct: float}"
)


def run() -> dict:
    hoje = date.today()
    sete_dias = (hoje - timedelta(days=7)).isoformat()

    dados = query("""
        SELECT p.nome, pr.data, pr.quantidade_produzida, pr.quantidade_consumida, pr.sobra
        FROM producao pr
        JOIN pratos p ON p.id = pr.prato_id
        WHERE pr.data >= ?
        ORDER BY pr.data DESC
    """, (sete_dias,))

    if not dados:
        return {"resumo": "Sem histórico recente.", "media_diaria": 0,
                "dia_mais_forte": "N/A", "prato_mais_popular": "N/A", "taxa_desperdicio_pct": 0.0}

    resumo_bruto = json.dumps(dados, ensure_ascii=False)
    resultado = call(SYSTEM, f"Histórico 7 dias:\n{resumo_bruto}")
    resultado["dados_raw"] = dados
    return resultado
