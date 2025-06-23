"""
Constantes do projeto Sales Analysis API
Centraliza todas as configurações para fácil manutenção
"""

# ========================
# CONFIGURAÇÕES DO OLLAMA
# ========================
OLLAMA_MODEL = "qwen3:30b"  # Modelo especificado pelo usuário
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TEMPERATURE = 0

# ========================
# CONFIGURAÇÕES DO MCP
# ========================
MCP_SERVER_PORT = 8001
MCP_SERVER_URL = f"http://localhost:{MCP_SERVER_PORT}/mcp"
MCP_TRANSPORT = "streamable_http"

# ========================
# CONFIGURAÇÕES DA API
# ========================
API_TITLE = "Sales Analysis API"
API_DESCRIPTION = "API for analyzing sales data using natural language queries powered by Ollama + MCP"
API_VERSION = "1.0.0"
API_DEFAULT_PORT = 8080

# ========================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ========================
DATABASE_URL = "sqlite:///./sales.db"
DATABASE_FILE = "sales.db"

# ========================
# CONFIGURAÇÕES DE VALIDAÇÃO
# ========================
SALES_KEYWORDS = [
    'vendas', 'produto', 'cliente', 'faturamento', 'receita',
    'quantidade', 'data', 'período', 'categoria', 'preço',
    'sales', 'product', 'customer', 'revenue', 'quantity',
    'date', 'period', 'category', 'price', 'estatística',
    'statistics', 'trend', 'análise', 'analysis'
]

# ========================
# MENSAGENS DE ERRO
# ========================
ERROR_QUESTION_NOT_SALES_RELATED = (
    "Desculpe, só posso responder perguntas relacionadas aos dados de vendas. "
    "Tente perguntar sobre produtos, clientes, vendas, faturamento, etc."
)

ERROR_QUESTION_EMPTY = "Question cannot be empty"

ERROR_PROCESSING_QUESTION = "Desculpe, ocorreu um erro ao processar sua pergunta: {error}"

ERROR_QUESTION_NOT_RELATED = "Question not related to sales data"

# ========================
# CONFIGURAÇÕES DE LOGS
# ========================
LOG_LEVEL = "INFO"

# ========================
# LIMITES E PAGINAÇÃO
# ========================
DEFAULT_TOP_PRODUCTS_LIMIT = 5
MIN_TOP_PRODUCTS_LIMIT = 1
MAX_TOP_PRODUCTS_LIMIT = 20

# ========================
# PERÍODO DE ANÁLISE
# ========================
ANALYSIS_PERIOD_DAYS = 365  # 12 meses para pegar os dados de demonstração

# ========================
# INFORMAÇÕES DO MODELO
# ========================
MODEL_DISPLAY_NAME = f"ollama:{OLLAMA_MODEL}"
MODEL_DESCRIPTION = f"Local LLM {OLLAMA_MODEL} via Ollama" 