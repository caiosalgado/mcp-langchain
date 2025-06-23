"""
LangChain service for processing natural language questions about sales data
"""
import os
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from typing import Dict, Any

class SalesInsightsService:
    """Service for generating sales insights using LangChain"""
    
    def __init__(self, db: SQLDatabase):
        self.db = db
        self.llm = self._initialize_llm()
        self.sql_chain = self._create_sql_chain()
        self.answer_chain = self._create_answer_chain()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=api_key
        )
    
    def _create_sql_chain(self):
        """Create chain for generating SQL queries"""
        return create_sql_query_chain(self.llm, self.db)
    
    def _create_answer_chain(self):
        """Create chain for generating natural language answers"""
        answer_prompt = ChatPromptTemplate.from_template(
            """Baseado na pergunta do usuário e no resultado da consulta SQL, 
            forneça uma resposta clara e concisa em português brasileiro.

            Pergunta: {question}
            Resultado SQL: {result}
            
            Resposta:"""
        )
        
        return answer_prompt | self.llm | StrOutputParser()
    
    def _validate_question(self, question: str) -> bool:
        """Validate if question is related to sales data"""
        sales_keywords = [
            'vendas', 'produto', 'cliente', 'faturamento', 'receita',
            'quantidade', 'data', 'período', 'categoria', 'preço',
            'sales', 'product', 'customer', 'revenue', 'quantity',
            'date', 'period', 'category', 'price'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in sales_keywords)
    
    def get_sales_insight(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question and return insights about sales data.
        
        Args:
            question: Natural language question about sales
            
        Returns:
            Dictionary with the answer and metadata
        """
        try:
            # Validate question is related to sales
            if not self._validate_question(question):
                return {
                    "answer": "Desculpe, só posso responder perguntas relacionadas aos dados de vendas. "
                             "Tente perguntar sobre produtos, clientes, vendas, faturamento, etc.",
                    "question": question,
                    "sql_query": None,
                    "error": "Question not related to sales data"
                }
            
            # Generate SQL query
            sql_query = self.sql_chain.invoke({"question": question})
            
            # Execute SQL query
            sql_result = self.db.run(sql_query)
            
            # Generate natural language answer
            answer = self.answer_chain.invoke({
                "question": question,
                "result": sql_result
            })
            
            return {
                "answer": answer,
                "question": question,
                "sql_query": sql_query.strip(),
                "sql_result": sql_result,
                "error": None
            }
            
        except Exception as e:
            return {
                "answer": f"Desculpe, não consegui processar sua pergunta. Erro: {str(e)}",
                "question": question,
                "sql_query": None,
                "error": str(e)
            } 