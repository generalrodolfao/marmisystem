"""API FastAPI — expõe dados para o frontend."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
from datetime import date, timedelta
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.db import init_db, query, execute
from database.seed import seed

class PlanejamentoInput(BaseModel):
    data: str
    prato_id: int
    quantidade: int

app = FastAPI(title="Sistema de Marmitas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    try:
        init_db()
        # Não roda seed() na Vercel automaticamente para evitar timeouts e erros de escrita
        if not os.environ.get("VERCEL"):
            seed()
        else:
            print("Vercel detectada: pulando seed automático.")
    except Exception as e:
        print(f"Erro no startup: {e}")

@app.get("/api/health")
def health():
    """Verifica saúde do sistema e conexão com o banco."""
    return {"status": "ok", "db": "connected" if os.environ.get("DATABASE_URL") else "sqlite"}


@app.get("/api/dashboard")
def dashboard():
    hoje = date.today().isoformat()
    ontem = (date.today() - timedelta(days=1)).isoformat()

    producao_hoje = query("""
        SELECT p.nome, pr.quantidade_produzida, pr.quantidade_consumida, pr.sobra
        FROM producao pr JOIN pratos p ON p.id = pr.prato_id
        WHERE pr.data = ?
    """, (hoje,))

    producao_ontem = query("""
        SELECT p.nome, pr.quantidade_produzida, pr.quantidade_consumida, pr.sobra
        FROM producao pr JOIN pratos p ON p.id = pr.prato_id
        WHERE pr.data = ?
    """, (ontem,))

    previsao_hoje = query("""
        SELECT p.nome, pv.quantidade_prevista
        FROM previsao pv JOIN pratos p ON p.id = pv.prato_id
        WHERE pv.data = ?
    """, (hoje,))

    relatorio = query("""
        SELECT conteudo FROM relatorios
        WHERE tipo = 'diario'
        ORDER BY id DESC LIMIT 1
    """)

    relatorio_parsed = {}
    if relatorio:
        try:
            relatorio_parsed = json.loads(relatorio[0]["conteudo"])
        except Exception:
            pass

    total_produzido = sum(r["quantidade_produzida"] for r in producao_ontem)
    total_consumido = sum(r["quantidade_consumida"] for r in producao_ontem)
    total_sobra = sum(r["sobra"] for r in producao_ontem)

    return {
        "data": hoje,
        "producao_ontem": {
            "total_produzido": total_produzido,
            "total_consumido": total_consumido,
            "total_sobra": total_sobra,
            "eficiencia_pct": round((total_consumido / total_produzido * 100) if total_produzido else 0, 1),
            "pratos": producao_ontem,
        },
        "previsao_hoje": previsao_hoje,
        "alertas": relatorio_parsed.get("alertas", []),
        "destaque": relatorio_parsed.get("destaque", ""),
        "eficiencia_pct": relatorio_parsed.get("eficiencia_pct", 0),
    }


@app.get("/api/cardapio")
def cardapio():
    hoje = date.today().isoformat()
    tres_dias = (date.today() + timedelta(days=3)).isoformat()

    items = query("""
        SELECT c.data, p.nome, p.categoria, p.popularidade_score
        FROM cardapio c JOIN pratos p ON p.id = c.prato_id
        WHERE c.data > ? AND c.data <= ?
        ORDER BY c.data
    """, (hoje, tres_dias))

    agrupado = {}
    for item in items:
        d = item["data"]
        if d not in agrupado:
            agrupado[d] = []
        agrupado[d].append({
            "nome": item["nome"],
            "categoria": item["categoria"],
            "popularidade": item["popularidade_score"],
        })

    return {"dias": [{"data": d, "pratos": pratos} for d, pratos in sorted(agrupado.items())]}


@app.get("/api/historico")
def historico(dias: int = 30):
    desde = (date.today() - timedelta(days=dias)).isoformat()

    dados = query("""
        SELECT pr.data, p.nome, p.categoria,
               pr.quantidade_produzida, pr.quantidade_consumida, pr.sobra
        FROM producao pr JOIN pratos p ON p.id = pr.prato_id
        WHERE pr.data >= ?
        ORDER BY pr.data DESC
    """, (desde,))

    # Agregado por dia
    por_dia = {}
    for d in dados:
        dia = d["data"]
        if dia not in por_dia:
            por_dia[dia] = {"data": dia, "total_produzido": 0, "total_consumido": 0, "total_sobra": 0, "pratos": []}
        por_dia[dia]["total_produzido"] += d["quantidade_produzida"]
        por_dia[dia]["total_consumido"] += d["quantidade_consumida"]
        por_dia[dia]["total_sobra"] += d["sobra"]
        por_dia[dia]["pratos"].append(d["nome"])

    dias_lista = sorted(por_dia.values(), key=lambda x: x["data"], reverse=True)
    for d in dias_lista:
        total = d["total_produzido"]
        d["eficiencia_pct"] = round((d["total_consumido"] / total * 100) if total else 0, 1)

    return {"historico": dias_lista, "total_dias": len(dias_lista)}


@app.get("/api/relatorio")
def relatorio():
    rows = query("SELECT * FROM relatorios ORDER BY id DESC LIMIT 7")
    result = []
    for r in rows:
        try:
            result.append({"data": r["data"], "tipo": r["tipo"], "conteudo": json.loads(r["conteudo"])})
        except Exception:
            pass
    return {"relatorios": result}


@app.get("/api/pratos")
def get_pratos():
    return query("SELECT * FROM pratos ORDER BY nome")


@app.post("/api/planejamento")
def post_planejamento(inp: PlanejamentoInput):
    # 1. Garante que o prato está no cardápio desse dia
    existente = query("SELECT id FROM cardapio WHERE data = ? AND prato_id = ?", (inp.data, inp.prato_id))
    if not existente:
        execute("INSERT INTO cardapio (data, prato_id) VALUES (?, ?)", (inp.data, inp.prato_id))
    
    # 2. Insere ou atualiza a previsão como 'manual'
    execute("DELETE FROM previsao WHERE data = ? AND prato_id = ?", (inp.data, inp.prato_id))
    execute("INSERT INTO previsao (data, prato_id, quantidade_prevista, tipo) VALUES (?, ?, ?, 'manual')", 
            (inp.data, inp.prato_id, inp.quantidade))
    
    return {"status": "ok", "message": "Planejamento salvo com sucesso"}


@app.get("/api/planejamento/sugestao")
def get_sugestao(data: str, prato_id: int):
    # 1. Média histórica
    res_media = query("SELECT AVG(quantidade_consumida) as media FROM producao WHERE prato_id = ?", (prato_id,))
    media = res_media[0]["media"] if res_media and res_media[0]["media"] else 50
    
    # 2. Popularidade
    res_pop = query("SELECT popularidade_score FROM pratos WHERE id = ?", (prato_id,))
    pop = res_pop[0]["popularidade_score"] if res_pop else 0.5
    
    # 3. Multiplicador de dia
    import datetime
    try:
        dt = datetime.datetime.strptime(data, "%Y-%m-%d")
        dow = dt.weekday()
        mult = 1.25 if dow == 0 else 1.30 if dow == 4 else 1.0 # Exemplo de ajuste
    except:
        mult = 1.0
        
    sugestao = int(media * mult * (pop + 0.5))
    return {"sugestao": sugestao}


@app.post("/api/pipeline/run")
def run_pipeline():
    from agents.commander import executar_pipeline
    resultado = executar_pipeline()
    return {"status": "ok", "resultado": resultado}
