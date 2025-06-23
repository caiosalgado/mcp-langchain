"""
FastAPI Sales Analysis API

This API provides two main endpoints:
1. GET /sales-insights?question={question} - Process natural language questions about sales data
2. GET /top-products - Get the top 5 products sold in the last month
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db, create_db_and_tables
from app.services import SalesService
from app.ollama_mcp_service import get_ollama_mcp_service
from app.constants import (
    API_TITLE, API_DESCRIPTION, API_VERSION,
    ERROR_QUESTION_EMPTY, ERROR_QUESTION_NOT_RELATED,
    DEFAULT_TOP_PRODUCTS_LIMIT, MIN_TOP_PRODUCTS_LIMIT, MAX_TOP_PRODUCTS_LIMIT,
    OLLAMA_MODEL, MODEL_DESCRIPTION
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    logger.info(f"Starting up {API_TITLE} with {MODEL_DESCRIPTION}...")
    
    # Create database tables
    create_db_and_tables()
    logger.info("Database tables created")
    
    logger.info(f"API started successfully using {OLLAMA_MODEL}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": API_TITLE,
        "description": API_DESCRIPTION,
        "endpoints": {
            "/sales-insights": "Process natural language questions about sales data",
            "/top-products": "Get top 5 products sold in the last month",
            "/stats": "Get general sales statistics",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        },
        "version": API_VERSION,
        "model": MODEL_DESCRIPTION
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ollama_mcp": "ready",
            "database": "ready"
        },
        "model": OLLAMA_MODEL
    }

@app.get("/sales-insights")
async def get_sales_insights(
    question: str = Query(..., description="Natural language question about sales data"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process natural language questions about sales data using Ollama + MCP.
    
    This endpoint uses Ollama (local LLM) with MCP (Model Context Protocol) 
    to force the model to search information directly from the database rather than 
    answering without context.
    
    Args:
        question: Natural language question about sales, products, customers, etc.
        
    Returns:
        Dictionary containing the answer, original question, MCP tools used, and metadata
        
    Example questions:
        - "Qual foi o produto mais vendido na última semana?"
        - "Quantos clientes fizeram compras este mês?"
        - "Qual categoria de produto teve maior faturamento?"
    """
    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail=ERROR_QUESTION_EMPTY
        )
    
    try:
        logger.info(f"Processing question with {OLLAMA_MODEL}+MCP: {question}")
        
        # Get the Ollama MCP service
        ollama_service = await get_ollama_mcp_service()
        
        # Process the question
        result = await ollama_service.get_sales_insight(question)
        
        if result.get("error") and ERROR_QUESTION_NOT_RELATED in result.get("error", ""):
            # Return 400 for questions not related to sales
            raise HTTPException(
                status_code=400,
                detail=result["answer"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/top-products")
async def get_top_products(
    limit: int = Query(
        DEFAULT_TOP_PRODUCTS_LIMIT, 
        ge=MIN_TOP_PRODUCTS_LIMIT, 
        le=MAX_TOP_PRODUCTS_LIMIT, 
        description="Number of top products to return"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get top products by quantity sold in the last month.
    
    Args:
        limit: Number of top products to return (1-20, default: 5)
        
    Returns:
        Dictionary with top products and metadata
    """
    try:
        logger.info(f"Getting top {limit} products")
        sales_service = SalesService(db)
        products = sales_service.get_top_products_last_month(limit)
        
        return {
            "top_products": products,
            "limit": limit,
            "period": "Last 12 months",
            "total_found": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/stats")
async def get_sales_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get general sales statistics.
    
    Returns:
        Dictionary with various sales statistics
    """
    try:
        logger.info("Getting sales statistics")
        sales_service = SalesService(db)
        stats = sales_service.get_sales_stats()
        
        return {
            "statistics": stats,
            "message": "Sales statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting sales stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 