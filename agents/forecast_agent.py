"""Agente de Previsão — calcula quantidade para os próximos 3 dias."""
import json
from datetime import date, timedelta
from database.db import query, execute
from agents.base_agent import call

SYSTEM = (
    "Você é o Analista de Demanda de Marmitas. "
    "Com base na média de consumo histórico e popularidade dos pratos, calcule a previsão. "
    "Adicione margem de segurança de 10% para dias de alta demanda (sexta/segunda). "
    "Retorne APENAS JSON: {previsoes: [{data, prato, quantidade, margem_pct}]}"
)

DOW_LABEL = {0: "segunda", 1: "terca", 2: "quarta", 3: "quinta", 4: "sexta", 5: "sabado", 6: "domingo"}


def run() -> dict:
    hoje = date.today()

    # Médias históricas por prato
    medias = query("""
        SELECT p.nome, AVG(pr.quantidade_consumida) as media, p.popularidade_score
        FROM producao pr JOIN pratos p ON p.id = pr.prato_id
        GROUP BY p.id
    """)

    # Cardápio dos próximos 3 dias
    proximos = []
    for i in range(1, 4):
        d = hoje + timedelta(days=i)
        pratos = query("""
            SELECT p.nome FROM cardapio c
            JOIN pratos p ON p.id = c.prato_id
            WHERE c.data = ?
        """, (d.isoformat(),))
        proximos.append({"data": d.isoformat(), "dia": DOW_LABEL[d.weekday()], "pratos": [p["nome"] for p in pratos]})

    user_msg = (
        f"Médias históricas: {json.dumps([{'prato': m['nome'], 'media': round(m['media'] or 0), 'popularidade': m['popularidade_score']} for m in medias], ensure_ascii=False)}\n"
        f"Cardápio próximos 3 dias: {json.dumps(proximos, ensure_ascii=False)}"
    )

    resultado = call(SYSTEM, user_msg, max_tokens=700)

    # Persiste previsões (apenas se não houver planejamento manual para o prato e data)
    for prev in resultado.get("previsoes", []):
        rows = query("SELECT id FROM pratos WHERE nome=?", (prev.get("prato", ""),))
        if rows:
            prato_id = rows[0]["id"]
            data = prev["data"]
            # Verifica se já existe um planejamento MANUAL
            manual_exists = query("SELECT id FROM previsao WHERE data=? AND prato_id=? AND tipo='manual'", (data, prato_id))
            if not manual_exists:
                # Remove automáticas anteriores e insere nova
                execute("DELETE FROM previsao WHERE data=? AND prato_id=? AND tipo='auto'", (data, prato_id))
                execute("INSERT INTO previsao (data, prato_id, quantidade_prevista, tipo) VALUES (?,?,?, 'auto')",
                        (data, prato_id, prev.get("quantidade", 0)))

    return resultado
