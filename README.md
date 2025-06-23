# Sales Analysis API - LLM + MCP Integration

Uma API REST construída com FastAPI que utiliza **Ollama (LLM local)** + **MCP (Model Context Protocol)** para processar perguntas em linguagem natural sobre dados de vendas com **alta precisão** e **timestamp-safe queries**.

## 🎯 Objetivo

Esta API fornece insights sobre dados de vendas através de:
- **Processamento de linguagem natural**: Use um modelo LLM local (Ollama) para fazer perguntas sobre vendas em português ou inglês
- **MCP (Model Context Protocol)**: Protocolo padronizado para conectar o LLM ao banco de dados
- **RAG (Retrieval-Augmented Generation)**: O modelo é forçado a buscar informações diretamente do banco de dados
- **Timestamp-Safe Queries**: Correção automática de bugs comuns em consultas de data com timestamps
- **Dados limpos**: Usa apenas os dados exatos do `script_dump_banco.txt` fornecido

## 🚀 Funcionalidades

### Endpoints Principais

1. **GET /sales-insights?question={question}**
   - Processa perguntas em linguagem natural sobre dados de vendas
   - Utiliza Ollama (modelo local qwen3:30b) com MCP para converter perguntas em consultas SQL
   - **5 ferramentas MCP especializadas** para diferentes tipos de consulta
   - Retorna respostas em português brasileiro com contexto temporal

2. **GET /top-products**
   - Retorna os 5 produtos mais vendidos no último período

3. **GET /stats**
   - Retorna estatísticas gerais de vendas

4. **Interface de Chat Interativo**
   - Execute `uv run python chat.py` para interface terminal em português
   - Conversação natural com tratamento de erros
   - Comandos: 'sair', 'help', 'ajuda'

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
git clone https://github.com/caiosalgado/mcp-langchain.git
cd mcp-langchain
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

O servidor MCP fornece **5 ferramentas especializadas**:
- 🔍 `query_sales_data`: Executa consultas SQL SELECT customizadas
- 📋 `get_database_schema`: Retorna estrutura do banco com avisos sobre timestamps
- 📊 `get_sales_statistics`: Estatísticas gerais de vendas
- 📈 `analyze_sales_trends`: Análise de tendências mensais
- ⭐ **`get_sales_by_period`: Consultas seguras por período (NOVA!)**

#### 🎯 **Nova Ferramenta - get_sales_by_period**
Esta ferramenta **corrige automaticamente** o bug comum de `BETWEEN` com timestamps:

**❌ Problema anterior:** 
```sql
-- Bug: Perdia vendas com timestamp diferente de 00:00:00
WHERE sale_date BETWEEN '2025-02-01' AND '2025-02-28'
-- Resultado: 17 vendas (incorreto)
```

**✅ Solução automática:**
```sql  
-- Usa funções seguras do SQLite
WHERE strftime('%Y-%m', sale_date) = '2025-02'
-- Resultado: 18 vendas (correto)
```

**Suporte para:**
- Períodos mensais: `get_sales_by_period('month', '2025-02')`
- Períodos diários: `get_sales_by_period('day', '2025-02-28')`
- Períodos anuais: `get_sales_by_period('year', '2025')`
- Períodos semanais: `get_sales_by_period('week', '2025-02-24')`

### 5. Inicie a API FastAPI
Em outro terminal:
```bash
# Inicia a API na porta 8000
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Use a Interface de Chat (Opcional)
```bash
# Interface interativa em português
uv run python chat.py
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

# ⭐ TESTE DA NOVA FUNCIONALIDADE - Períodos com timestamps
curl "http://localhost:8000/sales-insights?question=quantas vendas ocorreram em fevereiro de 2025"

# Pergunta sobre cliente
curl "http://localhost:8000/sales-insights?question=Quem comprou mais produtos?"

# Pergunta sobre faturamento
curl "http://localhost:8000/sales-insights?question=Qual é o faturamento total?"
```

### 4. Exemplos de perguntas suportadas:
- "Qual foi o produto mais vendido?"
- "Quantos clientes fizeram compras?"
- "Qual categoria teve maior faturamento?"
- **"Quantas vendas ocorreram em fevereiro de 2025?"** ⭐ (NOVO - timestamp-safe)
- **"Quais foram as vendas do dia 28 de fevereiro?"** ⭐ (NOVO - timestamp-safe)
- "Qual cliente gastou mais dinheiro?"
- "Quantos produtos de cada categoria foram vendidos?"

## 📊 Estrutura do Banco de Dados

### Tabelas:
- **products**: 5 produtos (SKU001-SKU005)
- **customers**: 5 clientes
- **sales**: 33 vendas (**com timestamps completos YYYY-MM-DD HH:MM:SS**)

### ⚠️ **Importante - Timestamps:**
A coluna `sale_date` contém timestamps completos, não apenas datas. A nova ferramenta `get_sales_by_period` trata isso automaticamente.

### Dados de exemplo:
```sql
-- Produtos
Product A (Category 1) - $10.99
Product B (Category 1) - $20.50
Product C (Category 2) - $15.75
Product D (Category 3) - $30.00
Product E (Category 4) - $25.00

-- Período de vendas (com timestamps)
2025-01-05 08:30:00 a 2025-03-02 16:45:30
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
│   SQLAlchemy    │    │   LangChain      │    │   MCP Tools     │
│   Models        │    │   + Ollama       │    │   (mcp_tools.py)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   SQLite DB     │
                                                │   (sales.db)    │
                                                └─────────────────┘
```

### 📁 **Nova Estrutura de Arquivos:**
```
mcp-langchain/
├── mcp_server.py        # 🚀 Servidor MCP principal
├── mcp_tools.py         # 🔧 5 ferramentas MCP organizadas (NOVO)
├── chat.py              # 💬 Interface de chat interativo (NOVO)
├── app/
│   ├── main.py          # FastAPI endpoints
│   ├── ollama_mcp_service.py  # Integração Ollama+MCP
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Configuração do banco
│   └── constants.py     # Configurações centralizadas
└── sales.db             # Banco SQLite
```

## 📝 Logs e Debugging

### Ver logs da API:
```bash
# Os logs aparecem no terminal onde você executou uvicorn
# Busque por "Loaded 5 MCP tools" para confirmar a nova ferramenta
```

### Ver logs do MCP Server:
```bash
# Os logs aparecem no terminal onde você executou mcp_server.py
# Confirme que mostra "get_sales_by_period: Get sales for specific periods"
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

### ⭐ **Problema: Contagem de vendas incorreta por período**
**Solução:** A nova ferramenta `get_sales_by_period` resolve automaticamente! Se ainda ocorrer, verifique se está usando a versão mais recente.

## 📚 Documentação da API

Acesse a documentação interativa em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Exemplos de Uso

### Chat Interativo:
```bash
uv run python chat.py

💬 Você: quantas vendas ocorreram em fevereiro de 2025
🤖 Resposta: Em fevereiro de 2025, houve **18 vendas** registradas no sistema.

📊 Detalhes complementares:
- **Itens vendidos**: 60 unidades
- **Faturamento total**: R$ 1.159,59
- **Ticket médio**: R$ 64,42
- **Período analisado**: 01/02/2025 a 28/02/2025
```

### Análise de Vendas via API:
```python
import requests

# Pergunta sobre análise de vendas
response = requests.get(
    "http://localhost:8000/sales-insights",
    params={"question": "Quantas vendas em fevereiro de 2025?"}
)

print(response.json())
```

### Resposta esperada:
```json
{
  "question": "Quantas vendas em fevereiro de 2025?",
  "answer": "Em fevereiro de 2025, houve **18 vendas** registradas no sistema...",
  "mcp_tools_used": ["get_sales_by_period", "get_sales_statistics"],
  "model_used": "ollama:qwen3:30b",
  "context_date": "23 de junho de 2025",
  "data_availability": "Os dados de vendas cobrem o período de janeiro a março de 2025 (56 dias de dados)",
  "error": null
}
```

## 🔒 Limitações de Segurança

- O MCP Server aceita apenas consultas SELECT por segurança
- Perguntas não relacionadas a vendas são rejeitadas automaticamente
- Validação de entrada em todos os endpoints
- **Timestamp-safe queries** previnem SQL injection em consultas de data

## ⭐ **Novidades da Versão Atual**

### 🆕 **get_sales_by_period Tool**
- ✅ **Correção automática** de bugs de timestamp
- ✅ **Precisão 100%** em consultas por período
- ✅ **Suporte para** mês, dia, ano e semana
- ✅ **Respostas em português** com detalhes completos

### 🔧 **Refatoração de Código**
- ✅ **mcp_tools.py** - Todas as ferramentas organizadas
- ✅ **mcp_server.py** - Servidor mais limpo
- ✅ **Melhor manutenibilidade** e extensibilidade

### 💬 **Interface de Chat**
- ✅ **chat.py** - Terminal interativo
- ✅ **Comandos em português** (sair, ajuda)
- ✅ **Tratamento de erros** robusto

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
⭐ **Timestamp-Safe**: Correção de bugs de consultas de data  
⭐ **5 Ferramentas MCP**: Análise especializada e robusta  
⭐ **Interface Chat**: Experiência de usuário aprimorada  

---

## 💡 Próximos Passos

- Adicionar mais tipos de análises
- Implementar cache para consultas frequentes  
- Adicionar testes automatizados
- Melhorar tratamento de erros
- Adicionar métricas de performance
- **Dashboard web interativo**
- **Exportação de relatórios**
