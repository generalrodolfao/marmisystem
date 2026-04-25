import sys
import os

# Adiciona a raiz ao path para encontrar as pastas database e agents
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from services.api import app
except Exception as e:
    import traceback
    print("ERRO CRÍTICO NA INICIALIZAÇÃO:")
    traceback.print_exc()
    raise e
