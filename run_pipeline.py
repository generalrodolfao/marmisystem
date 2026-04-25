#!/usr/bin/env python3
"""Executa o pipeline diário manualmente."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("❌ ANTHROPIC_API_KEY não definida. Crie um arquivo .env com a chave.")
    sys.exit(1)

from agents.commander import executar_pipeline

if __name__ == "__main__":
    executar_pipeline()
