"""Agente Comandante — orquestra o pipeline diário."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import init_db
from database.seed import seed
from agents import history_agent, menu_agent, forecast_agent, optimization_agent, reports_agent


def executar_pipeline() -> dict:
    print("\n🎖️  SISTEMA DE MARMITAS — PIPELINE DIÁRIO\n" + "="*45)

    init_db()
    seed()

    print("\n[1/5] Agente de Histórico...")
    hist = history_agent.run()
    print(f"      ✓ Média diária: {hist.get('media_diaria')} | Desperdício: {hist.get('taxa_desperdicio_pct')}%")

    print("[2/5] Agente de Cardápio...")
    menu = menu_agent.run()
    dias = menu.get("dias", [])
    print(f"      ✓ Cardápio gerado para {len(dias)} dias")

    print("[3/5] Agente de Previsão...")
    prev = forecast_agent.run()
    previsoes = prev.get("previsoes", [])
    print(f"      ✓ {len(previsoes)} previsões calculadas")

    print("[4/5] Agente de Otimização...")
    otim = optimization_agent.run()
    print(f"      ✓ Acurácia: {otim.get('acuracia_pct')}% | Alerta: {otim.get('alerta') or 'nenhum'}")

    print("[5/5] Agente de Relatórios...")
    relat = reports_agent.run(hist, prev, otim)
    print(f"      ✓ {relat.get('titulo')}")

    print("\n" + "="*45)
    print("✅  MISSÃO CUMPRIDA\n")

    return {
        "historico": hist,
        "cardapio": menu,
        "previsao": prev,
        "otimizacao": otim,
        "relatorio": relat,
    }


if __name__ == "__main__":
    resultado = executar_pipeline()
    import json
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
