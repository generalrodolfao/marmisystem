"""Agente de Cardápio — gera menu para os próximos 3 dias."""
import json
from datetime import date, timedelta
from database.db import query, execute
from agents.base_agent import call

SYSTEM = (
    "Você é o Chef Estratégico de Marmitas. "
    "Com base nos pratos disponíveis e no cardápio recente, sugira cardápio para os próximos 3 dias. "
    "Evite repetir prato em menos de 3 dias. Garanta variedade de categorias. "
    "Retorne APENAS JSON: {dias: [{data: 'YYYY-MM-DD', pratos: [nome1, nome2, nome3]}]}"
)


def run() -> dict:
    hoje = date.today()
    tres_dias_atras = (hoje - timedelta(days=3)).isoformat()

    pratos = query("SELECT nome, categoria, popularidade_score FROM pratos ORDER BY popularidade_score DESC")
    recentes = query("""
        SELECT p.nome, c.data FROM cardapio c
        JOIN pratos p ON p.id = c.prato_id
        WHERE c.data >= ?
    """, (tres_dias_atras,))

    dias_alvo = [(hoje + timedelta(days=i+1)).isoformat() for i in range(3)]

    user_msg = (
        f"Pratos disponíveis: {json.dumps([p['nome'] for p in pratos], ensure_ascii=False)}\n"
        f"Cardápio recente (evitar repetição): {json.dumps([r['nome'] for r in recentes], ensure_ascii=False)}\n"
        f"Gerar para os dias: {json.dumps(dias_alvo)}"
    )

    resultado = call(SYSTEM, user_msg, max_tokens=600)

    # Persiste no banco
    dias = resultado.get("dias", [])
    for dia_info in dias:
        data = dia_info.get("data")
        # Remove entradas anteriores para esse dia (idempotente)
        from database.db import get_conn
        conn = get_conn()
        conn.execute("DELETE FROM cardapio WHERE data=?", (data,))
        conn.commit()
        conn.close()
        for nome_prato in dia_info.get("pratos", []):
            rows = query("SELECT id FROM pratos WHERE nome=?", (nome_prato,))
            if rows:
                execute("INSERT INTO cardapio (data, prato_id) VALUES (?,?)", (data, rows[0]["id"]))

    return resultado
