"""
Ollama + MCP Service for processing natural language questions about sales data
Uses local Ollama model with MCP to access database
"""
import asyncio
import logging
import datetime
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

from app.constants import (
    OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TEMPERATURE,
    MCP_SERVER_URL, MCP_TRANSPORT,
    SALES_KEYWORDS, ERROR_QUESTION_NOT_SALES_RELATED,
    ERROR_QUESTION_NOT_RELATED, ERROR_PROCESSING_QUESTION,
    MODEL_DISPLAY_NAME
)

logger = logging.getLogger(__name__)

def _get_current_datetime() -> str:
    """Get current date and time formatted for the prompt"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def _get_current_date() -> str:
    """Get current date formatted for the prompt"""
    import locale
    try:
        # Tentar definir locale para português
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        # Fallback se não conseguir definir locale
        pass
    
    today = datetime.datetime.now()
    # Mapear meses manualmente para garantir português
    months_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    day = today.day
    month = months_pt[today.month]
    year = today.year
    
    return f"{day} de {month} de {year}"

class OllamaMCPSalesService:
    """Service for generating sales insights using Ollama + MCP"""
    
    def __init__(self):
        self.llm = None
        self.mcp_client = None
        self.agent = None
        self._initialized = False
        self.system_prompt_template = None
    
    def _create_system_prompt_with_date(self) -> str:
        """Create system prompt with current date and context"""
        current_date = _get_current_date()
        current_datetime = _get_current_datetime()
        
        system_prompt = f"""Você é um especialista em análise de dados de vendas.

CONTEXTO TEMPORAL:
- Data atual: {current_date}
- Data/hora atual: {current_datetime}
- Quando o usuário mencionar "hoje", "esta semana", "este mês" ou "período recente", use a data atual como referência.

INSTRUÇÕES:
1. Responda sempre em português brasileiro
2. Use as ferramentas MCP disponíveis para consultar o banco de dados
3. Seja preciso com datas e períodos ao fazer consultas SQL
4. Se os dados não cobrirem o período solicitado, explique claramente

IMPORTANTE: Os dados de vendas no banco cobrem o período de janeiro 2025 a março 2025. Se o usuário perguntar sobre períodos fora dessa faixa, informe sobre a limitação dos dados disponíveis.

Responda de forma clara e objetiva."""

        return system_prompt

    async def initialize(self):
        """Initialize the Ollama model and MCP client"""
        if self._initialized:
            return
        
        try:
            # Initialize Ollama chat model
            self.llm = ChatOllama(
                model=OLLAMA_MODEL,
                temperature=OLLAMA_TEMPERATURE,
                base_url=OLLAMA_BASE_URL
            )
            
            # Test Ollama connection
            try:
                test_response = await self._test_ollama_connection()
                logger.info(f"Ollama connection successful with {OLLAMA_MODEL}: {test_response[:100]}...")
            except Exception as e:
                logger.warning(f"Ollama connection test failed: {e}")
                # Try using the same model (since it's configured in constants)
                self.llm = ChatOllama(
                    model=OLLAMA_MODEL,
                    temperature=OLLAMA_TEMPERATURE,
                    base_url=OLLAMA_BASE_URL
                )
            
            # Initialize MCP client
            self.mcp_client = MultiServerMCPClient({
                "sales_db": {
                    "url": MCP_SERVER_URL,
                    "transport": MCP_TRANSPORT
                }
            })
            
            # Get tools from MCP server
            tools = await self.mcp_client.get_tools()
            logger.info(f"Loaded {len(tools)} MCP tools")
            
            # Create custom prompt template with current date
            system_prompt = self._create_system_prompt_with_date()
            
            # Create custom ChatPromptTemplate with date context
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("placeholder", "{messages}"),
            ])
            
            # Create agent with tools and custom prompt
            self.agent = create_react_agent(self.llm, tools, prompt=prompt_template)
            
            self._initialized = True
            logger.info(f"OllamaMCPSalesService initialized successfully with {OLLAMA_MODEL} and date context")
            
        except Exception as e:
            logger.error(f"Failed to initialize OllamaMCPSalesService: {e}")
            raise
    
    async def _test_ollama_connection(self) -> str:
        """Test connection to Ollama"""
        response = await self.llm.ainvoke("Hello")
        return response.content if hasattr(response, 'content') else str(response)
    
    def _validate_question(self, question: str) -> bool:
        """Validate if question is related to sales data"""
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in SALES_KEYWORDS)
    
    async def get_sales_insight(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question and return insights about sales data.
        
        Args:
            question: Natural language question about sales
            
        Returns:
            Dictionary with the answer and metadata
        """
        try:
            # Ensure service is initialized
            await self.initialize()
            
            # Validate question is related to sales
            if not self._validate_question(question):
                return {
                    "answer": ERROR_QUESTION_NOT_SALES_RELATED,
                    "question": question,
                    "mcp_tools_used": [],
                    "error": ERROR_QUESTION_NOT_RELATED,
                    "context_date": _get_current_date()
                }
            
            # Use the agent to process the question
            logger.info(f"Processing question with {OLLAMA_MODEL}+MCP and date context: {question}")
            
            # Invoke the agent with current date context
            result = await self.agent.ainvoke({
                "messages": [("human", question)]
            })
            
            # Extract the answer from the agent's response
            if "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                answer = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                answer = "Não consegui processar sua pergunta adequadamente."
            
            # Get tools safely
            mcp_tools = []
            if self.mcp_client:
                try:
                    tools = await self.mcp_client.get_tools()
                    mcp_tools = [tool.name for tool in tools]
                except Exception as e:
                    logger.warning(f"Could not get MCP tools: {e}")
            
            return {
                "answer": answer,
                "question": question,
                "mcp_tools_used": mcp_tools,
                "error": None,
                "model_used": MODEL_DISPLAY_NAME,
                "context_date": _get_current_date(),
                "context_datetime": _get_current_datetime()
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "answer": ERROR_PROCESSING_QUESTION.format(error=str(e)),
                "question": question,
                "mcp_tools_used": [],
                "error": str(e),
                "context_date": _get_current_date()
            }
    
    async def close(self):
        """Close connections"""
        if self.mcp_client:
            try:
                await self.mcp_client.close()
            except Exception as e:
                logger.warning(f"Error closing MCP client: {e}")

# Global instance
_service_instance: Optional[OllamaMCPSalesService] = None

async def get_ollama_mcp_service() -> OllamaMCPSalesService:
    """Get or create the global service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = OllamaMCPSalesService()
        await _service_instance.initialize()
    return _service_instance 