# Sales Analysis API - LLM + MCP Integration

Uma API REST construída com FastAPI que utiliza **Ollama (LLM local)** + **MCP (Model Context Protocol)** para processar perguntas em linguagem natural sobre dados de vendas.

## 🎯 O que é este projeto?

Esta API fornece insights sobre dados de vendas através de:
- **Processamento de linguagem natural**: Use um modelo LLM local (Ollama) para fazer perguntas sobre vendas em português
- **MCP (Model Context Protocol)**: Protocolo padronizado para conectar o LLM ao banco de dados
- **Interface de chat interativa**: Converse com seus dados de vendas naturalmente

## 🚀 Como instalar?

### 1. Instale o Ollama
```bash
# Instalar Ollama no Mac
brew install ollama

# Iniciar o serviço
ollama serve

# Em outro terminal, baixar o modelo
ollama pull qwen3:30b
```

### 2. Clone e configure o projeto
```bash
# Clonar repositório
git clone https://github.com/caiosalgado/mcp-langchain.git
cd mcp-langchain

# Instalar UV se não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependências
uv sync

# Configurar banco de dados
uv run python setup_clean_database.py
```

### 3. Inicie os serviços
```bash
# Terminal 1: Servidor MCP (porta 8001)
uv run python mcp_server.py --port 8001

# Terminal 2: API FastAPI (porta 8000)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Como usar?

### 1. Interface de Chat (Recomendado)
```bash
uv run python chat.py
```
Pergunte naturalmente sobre suas vendas:
- "Qual foi o produto mais vendido?"
- "Quantas vendas ocorreram em fevereiro de 2025?"
- "Quem são os melhores clientes?"
- "Qual é o faturamento total?"

### 2. API REST
```bash
# Testar funcionamento
curl http://localhost:8000/health

# Perguntas em linguagem natural
curl "http://localhost:8000/sales-insights?question=Qual foi o produto mais vendido?"

# Estatísticas básicas
curl http://localhost:8000/stats

# Top produtos
curl http://localhost:8000/top-products
```

## 📊 Dados incluídos

O projeto vem com dados de exemplo:
- 5 produtos (Product A-E)
- 5 clientes
- 33 vendas (período: janeiro-março 2025)

## 🛠️ Tecnologias

- **FastAPI**: API REST
- **Ollama**: LLM local (qwen3:30b)
- **MCP**: Protocolo para conectar LLM ao banco
- **SQLite**: Banco de dados
- **Python**: Linguagem principal
