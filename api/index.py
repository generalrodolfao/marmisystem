import sys
import os

# Adiciona a raiz ao path para encontrar as pastas database e agents
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.api import app
