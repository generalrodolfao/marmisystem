"""Base: chama Claude Haiku com prompt enxuto ou processa localmente."""
import json
import os
import anthropic
from datetime import date, datetime

# Mudar para False se quiser usar a API real
LOCAL_MODE = os.environ.get("LOCAL_MODE", "True").lower() == "true"

_client = None

def get_client():
    global _client
    if not _client:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client

MODEL = "claude-haiku-4-5-20251001"

def _call_local(system: str, user: str) -> dict:
    """Mock determinístico dos agentes para economizar tokens."""
    # 1. Agente de Histórico (Oficial de Dados)
    if "Oficial de Dados" in system:
        dados = json.loads(user.split(":\n")[1])
        if not dados:
            return {"resumo": "Sem dados.", "media_diaria": 0, "dia_mais_forte": "-", "prato_mais_popular": "-", "taxa_desperdicio_pct": 0}
        
        total_cons = sum(d["quantidade_consumida"] for d in dados)
        total_prod = sum(d["quantidade_produzida"] for d in dados)
        total_sobra = sum(d["sobra"] for d in dados)
        media = total_cons / len(set(d["data"] for d in dados))
        
        pratos_count = {}
        dias_count = {}
        for d in dados:
            pratos_count[d["nome"]] = pratos_count.get(d["nome"], 0) + d["quantidade_consumida"]
            dias_count[d["data"]] = dias_count.get(d["data"], 0) + d["quantidade_consumida"]
        
        mais_popular = max(pratos_count, key=pratos_count.get)
        mais_forte = max(dias_count, key=dias_count.get)
        
        return {
            "resumo": f"Consumo estável liderado por {mais_popular}.",
            "media_diaria": int(media),
            "dia_mais_forte": mais_forte,
            "prato_mais_popular": mais_popular,
            "taxa_desperdicio_pct": round((total_sobra / total_prod * 100), 2) if total_prod else 0
        }

    # 2. Agente de Cardápio (Chef Estratégico)
    if "Chef Estratégico" in system:
        try:
            # Tenta extrair a lista de pratos
            pratos_linha = [l for l in user.split("\n") if "Pratos disponíveis" in l][0]
            todos_pratos = json.loads(pratos_linha.split(": ", 1)[1])
            dias_linha = [l for l in user.split("\n") if "Gerar para os dias" in l][0]
            dias_alvo = json.loads(dias_linha.split(": ", 1)[1])
            recentes_linha = [l for l in user.split("\n") if "Cardápio recente" in l][0]
            recentes = json.loads(recentes_linha.split(": ", 1)[1])
        except Exception as e:
            return {"dias": []}

        disponiveis = [p for p in todos_pratos if p not in recentes]
        if not disponiveis: disponiveis = todos_pratos
        
        resp = {"dias": []}
        for idx, dia in enumerate(dias_alvo):
            selecionados = disponiveis[(idx*3):(idx*3)+3]
            if not selecionados: selecionados = todos_pratos[:3]
            resp["dias"].append({"data": dia, "pratos": selecionados})
        return resp

    # 3. Agente de Previsão (Analista de Demanda)
    if "Analista de Demanda" in system:
        try:
            medias_linha = [l for l in user.split("\n") if "Médias históricas" in l][0]
            medias = json.loads(medias_linha.split(": ", 1)[1])
            proximos_linha = [l for l in user.split("\n") if "Cardápio próximos 3 dias" in l][0]
            proximos = json.loads(proximos_linha.split(": ", 1)[1])
        except Exception as e:
            return {"previsoes": []}

        previsoes = []
        medias_dict = {m["prato"]: m["media"] for m in medias}
        pops_dict = {m["prato"]: m["popularidade"] for m in medias}
        
        for dia_data in proximos:
            dt = datetime.strptime(dia_data["data"], "%Y-%m-%d")
            dow = dt.weekday()
            mult_dow = 1.2 if dow in [0, 4] else 1.0 # Segunda e Sexta +20%
            
            for p in dia_data["pratos"]:
                base = medias_dict.get(p, 50)
                if not base: base = 50
                prod = int(base * mult_dow * (pops_dict.get(p, 0.5) + 0.5))
                previsoes.append({
                    "data": dia_data["data"],
                    "prato": p,
                    "quantidade": prod,
                    "margem_pct": 10 if dow in [0, 4] else 0
                })
        return {"previsoes": previsoes}

    # 4. Agente de Otimização (Controlador de Perdas)
    if "Controlador de Perdas" in system:
        try:
            dados = json.loads(user.split(":\n", 1)[1])
        except:
            return {"acuracia_pct": 0, "maior_desvio": "N/A", "sugestoes": [], "alerta": None}

        if not dados: return {"acuracia_pct": 0, "maior_desvio": "N/A", "sugestoes": [], "alerta": None}
        
        total_prev = sum(d["quantidade_prevista"] or 0 for d in dados)
        total_cons = sum(d["quantidade_consumida"] or 0 for d in dados)
        
        acuracia = (total_cons / total_prev * 100) if total_prev else 100
        if acuracia > 100: acuracia = max(0, 100 - (acuracia - 100))
        
        return {
            "acuracia_pct": round(acuracia, 1),
            "maior_desvio": "Sobra excessiva" if total_prev > total_cons else "Falta de pratos",
            "sugestoes": ["Ajustar margem de segurança", "Revisar popularidade"],
            "alerta": "Desvio significativo detectado" if abs(100 - acuracia) > 15 else None
        }

    # 5. Agente de Relatórios (Oficial de Comunicação)
    if "Oficial de Comunicação" in system:
        dados = json.loads(user)
        acuracia = dados.get("otimizacao", {}).get("acuracia_pct", 0)
        previsoes = dados.get('previsao_proximos_dias', [])
        destaque = previsoes[0].get('prato', 'N/A') if previsoes else 'N/A'
        
        return {
            "titulo": f"RELATÓRIO OPERACIONAL - {dados.get('data', 'HOJE')}",
            "resumo": f"Operação concluída com {acuracia}% de acurácia na previsão.",
            "alertas": [dados.get("otimizacao", {}).get("alerta")] if dados.get("otimizacao", {}).get("alerta") else [],
            "destaque": f"Prato destaque: {destaque}",
            "eficiencia_pct": acuracia
        }

    return {"error": "Agente desconhecido no modo local"}

def call(system: str, user: str, max_tokens: int = 512) -> dict:
    if LOCAL_MODE:
        return _call_local(system, user)

    resp = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = resp.content[0].text.strip()

    # Extrai JSON da resposta
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass

    # Tenta array JSON
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end:
            return {"items": json.loads(text[start:end])}
    except json.JSONDecodeError:
        pass

    return {"texto": text}
