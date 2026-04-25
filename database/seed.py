"""Popula o banco com 60 dias de histórico mockado."""
import random
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db import init_db, query, execute

PRATOS = [
    ("Arroz com Feijão e Bife",   "tradicional",  0.95),
    ("Frango Grelhado com Arroz", "tradicional",  0.90),
    ("Carne Assada",              "tradicional",  0.85),
    ("Macarrão ao Molho",         "massa",        0.70),
    ("Feijoada",                  "tradicional",  0.92),
    ("Peixe ao Forno",            "peixe",        0.65),
    ("Sopão de Legumes",          "sopa",         0.55),
    ("Risoto de Frango",          "massa",        0.72),
    ("Moqueca de Peixe",          "peixe",        0.68),
    ("Prato Vegetariano",         "vegetariano",  0.50),
]

# Multiplicador de demanda por dia (0=Seg, 6=Dom)
DIA_MULT = {0: 1.35, 1: 1.20, 2: 1.10, 3: 1.05, 4: 1.40, 5: 0.85, 6: 0.60}

BASE_DEMANDA = 100


def seed():
    init_db()

    if query("SELECT id FROM pratos LIMIT 1"):
        print("[seed] Banco já populado. Pulando.")
        return

    for nome, cat, pop in PRATOS:
        execute("INSERT INTO pratos (nome, categoria, popularidade_score) VALUES (?,?,?)",
                (nome, cat, pop))

    pratos = query("SELECT * FROM pratos")
    hoje = date.today()

    for i in range(60, 0, -1):
        dia = hoje - timedelta(days=i)
        dia_str = dia.isoformat()
        dow = dia.weekday()
        mult = DIA_MULT[dow]

        # Sorteia 2-3 pratos por dia
        num_pratos = 2 if dow == 6 else 3
        pratos_do_dia = random.sample(pratos, num_pratos)

        for prato in pratos_do_dia:
            execute("INSERT INTO cardapio (data, prato_id) VALUES (?,?)", (dia_str, prato["id"]))

            pop = prato["popularidade_score"]
            produzido = int(BASE_DEMANDA * mult * pop * random.uniform(0.9, 1.1))
            consumido = int(produzido * random.uniform(0.75, 0.98))
            sobra = produzido - consumido

            execute(
                "INSERT INTO producao (data, prato_id, quantidade_produzida, quantidade_consumida, sobra) VALUES (?,?,?,?,?)",
                (dia_str, prato["id"], produzido, consumido, sobra)
            )

    print(f"[seed] {len(pratos)} pratos e 60 dias de histórico criados.")


if __name__ == "__main__":
    seed()
