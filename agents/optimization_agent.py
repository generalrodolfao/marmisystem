"""Agente de Otimização — compara previsto vs real e sugere ajustes."""
import json
from datetime import date, timedelta
from database.db import query
from agents.base_agent import call

SYSTEM = (
    "Você é o Controlador de Perdas de Marmitas. "
    "Compare previsão vs produção real e identifique desvios. "
    "Retorne APENAS JSON: {acuracia_pct: float, maior_desvio: string, sugestoes: [string], alerta: string|null}"
)


def run() -> dict:
    sete_dias = (date.today() - timedelta(days=7)).isoformat()

    comparativo = query("""
        SELECT p.nome,
               pv.quantidade_prevista,
               pr.quantidade_consumida,
               pr.sobra,
               pr.data
        FROM producao pr
        JOIN pratos p ON p.id = pr.prato_id
        LEFT JOIN previsao pv ON pv.prato_id = pr.prato_id AND pv.data = pr.data
        WHERE pr.data >= ?
        ORDER BY pr.data DESC
    """, (sete_dias,))

    if not comparativo:
        return {"acuracia_pct": 0, "maior_desvio": "sem dados", "sugestoes": [], "alerta": None}

    resultado = call(SYSTEM, f"Comparativo previsto vs real:\n{json.dumps(comparativo, ensure_ascii=False)}")
    return resultado
