# 🎖️ SISTEMA DE PROVISIONAMENTO DE MARMITAS
## Operação: Alimentação Inteligente

## 🎯 Objetivo
Construir um sistema baseado em agentes para:
- Prever demanda diária de marmitas
- Sugerir cardápio com 3 dias de antecedência
- Manter histórico consistente (mesmo com dados mockados)
- Aprender com consumo real e melhorar previsões

---

# 🧠 ARQUITETURA DE AGENTES

## 👨‍✈️ 1. Agente Comandante (Orquestrador)
Responsável por coordenar todos os agentes.

### Funções:
- Executar pipeline diário
- Garantir ordem de execução
- Consolidar outputs
- Gerar relatório final

---

## 📊 2. Agente de Histórico (Data Officer)
Responsável por criar e manter base histórica.

### Funções:
- Criar dados mockados iniciais
- Registrar consumo diário real
- Armazenar:
  - prato
  - quantidade produzida
  - quantidade consumida
  - sobra
  - dia da semana
  - clima (mockado inicialmente)

### Regras:
- Sempre garantir pelo menos 30 dias de histórico
- Simular padrões realistas:
  - Segunda: alta demanda
  - Domingo: baixa demanda

---

## 🍛 3. Agente de Cardápio (Chef Estratégico)
Responsável por planejar cardápio.

### Funções:
- Gerar cardápio com 3 dias de antecedência
- Variar pratos evitando repetição
- Classificar pratos por:
  - popularidade
  - custo
  - tempo de preparo

### Regras:
- Não repetir prato em menos de 3 dias
- Garantir equilíbrio:
  - proteína
  - carboidrato
  - vegetariano (opcional)

---

## 📈 4. Agente de Previsão (Analista de Demanda)
Responsável por prever quantidade de marmitas.

### Inputs:
- Histórico de consumo
- Dia da semana
- Cardápio planejado

### Outputs:
- Quantidade prevista por prato
- Margem de segurança (%)

### Estratégia inicial:
- Média móvel simples (últimos 7 dias)
- Ajuste por popularidade do prato

---

## ⚖️ 5. Agente de Otimização (Controle de Perdas)
Responsável por reduzir desperdício.

### Funções:
- Comparar previsto vs real
- Ajustar fatores de previsão
- Sugerir melhorias

---

## 📢 6. Agente de Relatórios (Comunicação)
Responsável por gerar insights.

### Outputs:
- Relatório diário
- Relatório semanal
- Alertas:
  - excesso de sobra
  - falta de comida

---

# 🗄️ BANCO DE DADOS (PostgreSQL)

## Tabelas:

### pratos
- id
- nome
- categoria
- popularidade_score

### cardapio
- id
- data
- prato_id

### producao
- id
- data
- prato_id
- quantidade_produzida
- quantidade_consumida
- sobra

### previsao
- id
- data
- prato_id
- quantidade_prevista

---

# ⚙️ PIPELINE DIÁRIO

## Ordem de execução:

1. Agente de Histórico atualiza base
2. Agente de Cardápio gera próximos 3 dias
3. Agente de Previsão calcula demanda
4. Agente de Otimização ajusta parâmetros
5. Agente de Relatórios gera saída final

---

# 🧪 DADOS MOCKADOS

Gerar automaticamente:
- 60 dias de histórico
- Variação por dia da semana
- Popularidade de pratos:
  - Arroz e feijão: alta
  - Macarrão: média
  - Sopas: variável

---

# 🖥️ FRONTEND (React + Vite)

## Telas:

### Dashboard
- Quantidade prevista hoje
- Quantidade produzida vs consumida
- Alertas

### Cardápio
- Próximos 3 dias

### Histórico
- Gráficos de consumo

---

## 🎨 Identidade Visual

Inspirado nas forças armadas do Brasil:

### Cores:
- Verde oliva (#4B5320)
- Verde militar (#3C4F3D)
- Amarelo bandeira (#FFDF00)
- Branco

### Estilo:
- Minimalista
- Forte e objetivo
- Tipografia robusta

---

# 🧱 STACK

- Backend: Python
- Orquestração: Antigravity
- Agentes: Claude Code
- Banco: PostgreSQL
- Frontend: React + Vite

---

# 🤖 INSTRUÇÕES PARA CLAUDE

Você deve:

1. Criar estrutura de pastas:
   - agents/
   - services/
   - database/
   - frontend/

2. Implementar cada agente como módulo independente

3. Criar:
   - scripts de execução diária
   - API simples (FastAPI recomendado)

4. Garantir:
   - logs claros
   - outputs estruturados (JSON)

5. Simular execução completa do pipeline

---

# 🚀 EVOLUÇÕES FUTURAS

- Integração com clima real
- Machine Learning (ARIMA / Prophet)
- Integração com compras (estoque)
- Dashboard em tempo real

---

# 🎖️ MISSÃO

Minimizar desperdício.
Maximizar eficiência.
Garantir que ninguém fique sem comida.
