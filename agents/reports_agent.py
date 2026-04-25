"""Agente de Relatórios — gera relatório diário com alertas."""
import json
from datetime import date
from database.db import query, execute
from agents.base_agent import call

SYSTEM = (
    "Você é o Oficial de Comunicação do Sistema de Marmitas. "
    "Com base nos dados consolidados, gere um relatório diário objetivo. "
    "Retorne APENAS JSON: {titulo: string, resumo: string, alertas: [string], destaque: string, eficiencia_pct: float}"
)


def run(historico: dict, previsao: dict, otimizacao: dict) -> dict:
    contexto = {
        "data": date.today().isoformat(),
        "historico": {k: v for k, v in historico.items() if k != "dados_raw"},
        "previsao_proximos_dias": previsao.get("previsoes", [])[:3],
        "otimizacao": otimizacao,
    }

    resultado = call(SYSTEM, json.dumps(contexto, ensure_ascii=False), max_tokens=600)

    # Persiste relatório
    execute(
        "INSERT INTO relatorios (data, tipo, conteudo) VALUES (?,?,?)",
        (date.today().isoformat(), "diario", json.dumps(resultado, ensure_ascii=False))
    )

    return resultado
