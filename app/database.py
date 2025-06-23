"""
Database configuration and connection management
"""
import os
from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy import create_engine, func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from langchain_community.utilities import SQLDatabase
from app.constants import DATABASE_URL as DEFAULT_DATABASE_URL

# Get database URL from environment variable or use default from constants
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Create LangChain SQLDatabase instance
langchain_db = SQLDatabase(engine)

def create_db_and_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_langchain_db():
    """Get LangChain database instance"""
    return langchain_db

def get_sales_date_range() -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Get the actual date range of sales data from the database
    
    Returns:
        Tuple of (min_date, max_date) or (None, None) if no data
    """
    try:
        # Import here to avoid circular imports
        from app.models import Sale
        
        with SessionLocal() as session:
            # Query for min and max dates using SQLAlchemy
            result = session.execute(
                select(
                    func.min(Sale.sale_date).label('min_date'),
                    func.max(Sale.sale_date).label('max_date')
                )
            ).first()
            
            if result and result.min_date and result.max_date:
                return result.min_date, result.max_date
            else:
                return None, None
                
    except Exception as e:
        # Log error but don't crash
        print(f"Error getting sales date range: {e}")
        return None, None

def format_date_range_for_prompt(min_date: datetime, max_date: datetime) -> str:
    """
    Format date range for use in prompts
    
    Args:
        min_date: Earliest date in the data
        max_date: Latest date in the data
        
    Returns:
        Formatted string describing the data period
    """
    # Map months to Portuguese
    months_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    # Format dates
    min_month = months_pt[min_date.month]
    max_month = months_pt[max_date.month]
    
    if min_date.year == max_date.year:
        if min_date.month == max_date.month:
            # Same month and year
            return f"{min_month} de {min_date.year}"
        else:
            # Different months, same year
            return f"{min_month} a {max_month} de {min_date.year}"
    else:
        # Different years
        return f"{min_month} de {min_date.year} a {max_month} de {max_date.year}"

def get_sales_data_availability_info() -> str:
    """
    Get formatted information about sales data availability for prompts
    
    Returns:
        Formatted string describing data availability
    """
    min_date, max_date = get_sales_date_range()
    
    if min_date is None or max_date is None:
        return "Não há dados de vendas disponíveis no banco de dados."
    
    date_range = format_date_range_for_prompt(min_date, max_date)
    total_days = (max_date - min_date).days + 1
    
    return f"Os dados de vendas cobrem o período de {date_range} ({total_days} dias de dados)." 