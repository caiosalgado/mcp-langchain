# Sales Analysis API - Teste Técnico

Uma API REST construída com FastAPI que utiliza **Ollama (LLM local)** + **MCP (Model Context Protocol)** para processar perguntas em linguagem natural sobre dados de vendas.

## 🎯 Objetivo

Esta API fornece insights sobre dados de vendas através de:
- **Processamento de linguagem natural**: Use um modelo LLM local (Ollama) para fazer perguntas sobre vendas em português ou inglês
- **MCP (Model Context Protocol)**: Protocolo padronizado para conectar o LLM ao banco de dados
- **RAG (Retrieval-Augmented Generation)**: O modelo é forçado a buscar informações diretamente do banco de dados
- **Dados limpos**: Usa apenas os dados exatos do `script_dump_banco.txt` fornecido

## 🚀 Funcionalidades

### Endpoints Principais

1. **GET /sales-insights?question={question}**
   - Processa perguntas em linguagem natural sobre dados de vendas
   - Utiliza Ollama (modelo local qwen3:30b) com MCP para converter perguntas em consultas SQL
   - Retorna respostas em português brasileiro

2. **GET /top-products**
   - Retorna os 5 produtos mais vendidos no último período

3. **GET /stats**
   - Retorna estatísticas gerais de vendas

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno para APIs
- **Ollama**: Servidor de LLM local (modelo qwen3:30b)
- **MCP (Model Context Protocol)**: Protocolo para conectar LLM ao banco
- **FastMCP**: Implementação rápida do protocolo MCP
- **LangChain**: Framework para aplicações com LLMs
- **SQLite**: Banco de dados leve
- **SQLAlchemy**: ORM para Python
- **UV**: Gerenciador de dependências Python

## 📋 Pré-requisitos

### 1. Ollama
Instale o Ollama no seu Mac:
```bash
# Instalar Ollama
brew install ollama

# Iniciar o serviço
ollama serve

# Em outro terminal, baixar o modelo
ollama pull qwen3:30b
```

### 2. Python 3.8+
```bash
python --version
```

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <repository-url>
cd langchain_fastapi
```

### 2. Instale as dependências com UV
```bash
# Instalar UV se não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependências
uv sync
```

### 3. Configure o banco de dados
```bash
# Execute o script de configuração limpo
uv run python setup_clean_database.py
```

Este script cria o banco `sales.db` com exatamente os dados do `script_dump_banco.txt`:
- 5 produtos (Product A, B, C, D, E)
- 5 clientes (John Doe, Jane Smith, Bob Johnson, Alice Brown, Charlie Davis)
- 33 vendas (período: 2025-01-05 a 2025-03-02)

### 4. Inicie o servidor MCP
Em um terminal separado:
```bash
# Inicia o servidor MCP na porta 8001
uv run python mcp_server.py --port 8001
```

O servidor MCP fornece as seguintes ferramentas:
- `query_sales_data`: Executa consultas SQL SELECT
- `get_database_schema`: Retorna a estrutura do banco
- `get_sales_statistics`: Retorna estatísticas gerais
- `analyze_sales_trends`: Analisa tendências de vendas

### 5. Inicie a API FastAPI
Em outro terminal:
```bash
# Inicia a API na porta 8000
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testando a API

### 1. Verificar se está funcionando
```bash
curl http://localhost:8000/health
```

### 2. Testar endpoints básicos
```bash
# Estatísticas gerais
curl http://localhost:8000/stats

# Top produtos
curl http://localhost:8000/top-products
```

### 3. Testar perguntas em linguagem natural
```bash
# Pergunta sobre produto mais vendido
curl "http://localhost:8000/sales-insights?question=Qual foi o produto mais vendido?"

# Pergunta sobre cliente
curl "http://localhost:8000/sales-insights?question=Quem comprou mais produtos?"

# Pergunta sobre faturamento
curl "http://localhost:8000/sales-insights?question=Qual é o faturamento total?"
```

### 4. Exemplos de perguntas suportadas:
- "Qual foi o produto mais vendido?"
- "Quantos clientes fizeram compras?"
- "Qual categoria teve maior faturamento?"
- "Quais vendas foram feitas em janeiro?"
- "Qual cliente gastou mais dinheiro?"
- "Quantos produtos de cada categoria foram vendidos?"

## 📊 Estrutura do Banco de Dados

### Tabelas:
- **products**: 5 produtos (SKU001-SKU005)
- **customers**: 5 clientes
- **sales**: 33 vendas

### Dados de exemplo:
```sql
-- Produtos
Product A (Category 1) - $10.99
Product B (Category 1) - $20.50
Product C (Category 2) - $15.75
Product D (Category 3) - $30.00
Product E (Category 4) - $25.00

-- Período de vendas
2025-01-05 a 2025-03-02
```

## 🔧 Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Ollama MCP     │    │   MCP Server    │
│   (Port 8000)   │───▶│   Service        │───▶│   (Port 8001)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SQLAlchemy    │    │   LangChain      │    │   SQLite DB     │
│   Models        │    │   + Ollama       │    │   (sales.db)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📝 Logs e Debugging

### Ver logs da API:
```bash
# Os logs aparecem no terminal onde você executou uvicorn
```

### Ver logs do MCP Server:
```bash
# Os logs aparecem no terminal onde você executou mcp_server.py
```

### Verificar se Ollama está funcionando:
```bash
# Testar Ollama diretamente
ollama run qwen3:30b "Hello"
```

## 🐛 Solução de Problemas

### Problema: Ollama não conecta
```bash
# Verificar se Ollama está rodando
ps aux | grep ollama

# Reiniciar Ollama
ollama serve
```

### Problema: MCP Server não conecta
```bash
# Verificar se está rodando na porta 8001
lsof -i :8001

# Reiniciar o servidor MCP
uv run python mcp_server.py --port 8001
```

### Problema: Banco de dados vazio
```bash
# Recriar o banco limpo
uv run python setup_clean_database.py
```

## 📚 Documentação da API

Acesse a documentação interativa em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Exemplos de Uso

### Análise de Vendas:
```python
import requests

# Pergunta sobre análise de vendas
response = requests.get(
    "http://localhost:8000/sales-insights",
    params={"question": "Qual categoria de produto vendeu mais?"}
)

print(response.json())
```

### Resposta esperada:
```json
{
  "question": "Qual categoria de produto vendeu mais?",
  "answer": "Baseado nos dados, Category 4 (Product E) teve o maior volume de vendas...",
  "mcp_tools_used": ["query_sales_data", "get_sales_statistics"],
  "model_used": "ollama:qwen3:30b",
  "timestamp": "2025-01-17T10:30:00",
  "error": null
}
```

## 🔒 Limitações de Segurança

- O MCP Server aceita apenas consultas SELECT por segurança
- Perguntas não relacionadas a vendas são rejeitadas
- Validação de entrada em todos os endpoints

## 🎯 Teste Técnico - Checklist

✅ **FastAPI**: API REST funcional  
✅ **Banco de dados**: SQLite com dados do script fornecido  
✅ **SQLAlchemy**: ORM para consultas  
✅ **LLM Local**: Ollama (qwen3:30b)  
✅ **MCP**: Protocolo para conectar LLM ao banco  
✅ **RAG**: Modelo busca dados diretamente do banco  
✅ **Endpoints**: `/sales-insights` e `/top-products`  
✅ **Documentação**: README completo e comentários no código  
✅ **Limitação de RAG**: Modelo não responde sem contexto do banco  

---

## 💡 Próximos Passos

- Adicionar mais tipos de análises
- Implementar cache para consultas frequentes  
- Adicionar testes automatizados
- Melhorar tratamento de erros
- Adicionar métricas de performance
